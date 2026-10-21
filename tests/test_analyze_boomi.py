"""
Regression tests for analyzers/analyze_boomi.py.

Locks in a set of extraction bugs found by comparing a real migrated Workato
recipe against its source Boomi process ("Integration Troubleshooting -
Professional"): the Route shape's branch conditions, the Notify shape, the
Map shape's field mappings (including function-routed transformations), the
Stop shape's continue="false" hard-exit, and the generic silent-fallback for
any shape type with no extraction logic. Each fixture below is a trimmed-down
copy of real XML confirmed against the live-pulled Boomi components -- not
synthetic examples -- so a regression here means a real migration would
silently lose real business logic again.

No external test framework dependency (stdlib unittest only) since this
project has none set up. Run with:
    python -m unittest tests/test_analyze_boomi.py -v
"""
import os
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers import analyze_boomi as ab


def shape_from_xml(xml_str):
    return ET.fromstring(xml_str)


def traverse_from_process_xml(process_xml, component_index=None):
    """Parse a <shapes>...</shapes> fragment and run the real traversal path
    (_build_shape_map / _build_conn_map / _traverse), exactly like analyze_process
    does, instead of hand-building shape_map/conn_map dicts."""
    root = ET.fromstring(f"<process>{process_xml}</process>")
    all_shapes = root.findall(".//shape")
    shape_map = ab._build_shape_map(all_shapes)
    conn_map = ab._build_conn_map(all_shapes)
    start_name = all_shapes[0].get("name")
    return ab._traverse(start_name, shape_map, conn_map, component_index or {}, set())


class TestRouteConditionExtraction(unittest.TestCase):
    """Boomi's Route shape conditions live in <route><routeproperty>/<routevalues>,
    NOT in the <dragpoint> elements (which only carry branch keys/destinations).
    This was previously never read, so every route's branch conditions were
    silently absent from the spec."""

    ROUTE_SHAPE_XML = """
    <shape image="route_icon" name="shape18" shapetype="route" userlabel="" x="240.0" y="48.0">
      <configuration><route>
        <routeproperty valueType="profile">
          <profileelement elementId="46" elementName="Status__c (Contact/Status__c)"
                           profileId="780a2bff-e15f-4b37-8280-58cfcddb4cff" profileType="profile.xml"/>
        </routeproperty>
        <routevalues>
          <routevalue key="3" name="Equals Installed" qualifier="equals" value="Installed"/>
          <routevalue key="5" name="Equals New" qualifier="equals" value="New"/>
          <routevalue key="7" name="Equal To Cancelled" qualifier="equals" value="Cancelled"/>
        </routevalues>
      </route></configuration>
      <dragpoints>
        <dragpoint identifier="3" name="shape18.dragpoint1" text="1 - Equals Installed" toShape="shapeA"/>
        <dragpoint identifier="default" name="shape18.dragpoint2" text="Default" toShape="shapeB"/>
        <dragpoint identifier="7" name="shape18.dragpoint4" text="3 - Equal To Cancelled" toShape="shapeC"/>
      </dragpoints>
    </shape>
    """

    def test_extract_route_values_reads_field_and_branch_conditions(self):
        shape = shape_from_xml(self.ROUTE_SHAPE_XML)
        field_label, values = ab._extract_route_values(shape)
        self.assertEqual(field_label, "Status__c (Contact/Status__c)")
        self.assertEqual(values["3"], {"name": "Equals Installed", "qualifier": "equals", "value": "Installed"})
        self.assertEqual(values["7"]["value"], "Cancelled")

    def test_traverse_attaches_real_condition_strings_per_branch(self):
        stop_true = '<shape name="{n}" shapetype="stop"><configuration><stop continue="true"/></configuration><dragpoints/></shape>'
        process_xml = self.ROUTE_SHAPE_XML + "".join(
            stop_true.format(n=n) for n in ("shapeA", "shapeB", "shapeC")
        )
        steps, _ = traverse_from_process_xml(process_xml)
        self.assertEqual(len(steps), 1)
        router = steps[0]
        self.assertEqual(router["type"], "choice_router")
        self.assertFalse(router["requires_review"])  # real routevalues were found
        branches_by_id = {b["identifier"]: b for b in router["branches"]}
        self.assertEqual(
            branches_by_id["3"]["condition"],
            'Status__c (Contact/Status__c) equals "Installed"',
        )
        self.assertEqual(
            branches_by_id["7"]["condition"],
            'Status__c (Contact/Status__c) equals "Cancelled"',
        )
        self.assertEqual(branches_by_id["default"]["condition"], "default (no other branch matched)")


class TestDecisionConditionExtraction(unittest.TestCase):
    """The previous implementation searched for element names
    (<comparevalue>/<comparevalueoperator>/<compareto>) that don't exist
    anywhere in Boomi's real Decision schema, silently returning a bare
    operator string like "EQUALS" with no field or value for every single
    Decision shape. Confirmed against a real "Active Account?" shape pulled
    from a different live process (Integration Troubleshooting - Associate).
    Decision (plain if/else) is far more common across Boomi processes than
    Route, making this likely the highest-impact fix for future migrations."""

    DECISION_SHAPE_XML = """
    <shape image="decision_icon" name="shape27" shapetype="decision" userlabel="Active Account?" x="224.0" y="144.0">
      <configuration><decision comparison="equals" name="Active Account?">
        <decisionvalue valueType="profile">
          <profileelement elementId="12" elementName="Active (Account/Active)"
                           profileId="b2247321-adcc-4895-a8c4-b02e79dca539" profileType="profile.xml"/>
        </decisionvalue>
        <decisionvalue valueType="static">
          <staticparameter staticproperty="true"/>
        </decisionvalue>
      </decision></configuration>
      <dragpoints>
        <dragpoint identifier="true" name="shape27.dragpoint1" text="True" toShape="shapeT"/>
        <dragpoint identifier="false" name="shape27.dragpoint2" text="False" toShape="shapeF"/>
      </dragpoints>
    </shape>
    """

    def test_extract_decision_condition_reads_operator_attribute_and_both_operands(self):
        shape = shape_from_xml(self.DECISION_SHAPE_XML)
        condition = ab._extract_decision_condition(shape)
        self.assertEqual(condition, "Active (Account/Active) equals true")

    def test_traverse_decision_requires_review_false_when_resolved(self):
        stop_true = '<shape name="{n}" shapetype="stop"><configuration><stop continue="true"/></configuration><dragpoints/></shape>'
        process_xml = self.DECISION_SHAPE_XML + "".join(
            stop_true.format(n=n) for n in ("shapeT", "shapeF")
        )
        steps, _ = traverse_from_process_xml(process_xml)
        decision_step = next(s for s in steps if s.get("boomi_step") == "Decision")
        self.assertEqual(decision_step["condition"], "Active (Account/Active) equals true")
        self.assertFalse(decision_step["requires_review"])

    def test_decision_with_unresolvable_operand_is_surfaced_not_silently_empty(self):
        """An operand shape not seen in any real example yet (not profile/
        static/process/date) must still produce a visible marker string
        instead of silently falling back to an empty value."""
        xml = """
        <shape name="s1" shapetype="decision"><configuration><decision comparison="greaterthan">
          <decisionvalue valueType="exotic"><somefutureoperand foo="bar"/></decisionvalue>
          <decisionvalue valueType="static"><staticparameter staticproperty="5"/></decisionvalue>
        </decision></configuration><dragpoints/></shape>
        """
        shape = shape_from_xml(xml)
        condition = ab._extract_decision_condition(shape)
        self.assertIn("unrecognized", condition)
        self.assertIn("greaterthan", condition)


class TestNotifyShapeExtraction(unittest.TestCase):
    """shapetype="notify" previously had no dispatch branch in
    _classify_and_extract_shape at all, so it silently fell through to the
    terminal `return None` and the whole step -- and whatever alert it sent --
    vanished from the spec. This was confirmed live as the cause of a
    Cancelled-contact branch looking like a pure no-op when it actually fires
    a WARNING notification."""

    NOTIFY_SHAPE_XML = """
    <shape image="notify_icon" name="shape29" shapetype="notify" userlabel="" x="432.0" y="688.0">
      <configuration><notify disableEvent="true" enableUserLog="false" perExecution="false" title="">
        <notifyMessage>{1}</notifyMessage>
        <notifyMessageLevel>WARNING</notifyMessageLevel>
        <notifyParameters>
          <parametervalue key="0" usesEncryption="false" valueType="profile">
            <profileelement elementId="9" elementName="Name (Contact/Name)"
                             profileId="780a2bff-e15f-4b37-8280-58cfcddb4cff" profileType="profile.xml"/>
          </parametervalue>
        </notifyParameters>
      </notify></configuration>
      <dragpoints/>
    </shape>
    """

    def test_extract_notify_step_captures_message_and_level(self):
        shape = shape_from_xml(self.NOTIFY_SHAPE_XML)
        step = ab.extract_notify_step(shape, 1)
        self.assertEqual(step["type"], "logger")
        self.assertEqual(step["message_level"], "WARNING")
        self.assertEqual(step["message_template"], "{1}")
        self.assertEqual(step["message_parameters"], ["Name (Contact/Name)"])
        self.assertFalse(step["requires_review"])

    def test_classify_and_extract_shape_dispatches_notify_not_dropped(self):
        shape = shape_from_xml(self.NOTIFY_SHAPE_XML)
        step, seq = ab._classify_and_extract_shape(shape, {}, set(), 0)
        self.assertIsNotNone(step, "Notify step must not be silently dropped")
        self.assertEqual(step["type"], "logger")


class TestMapFieldMappingExtraction(unittest.TestCase):
    """extract_map_step previously only captured the bare map_id and never
    resolved it against the component index, so real field-to-field mappings
    -- including a JS concatenation and a Cross-Reference Lookup confirmed in
    a real transform.map component -- were entirely absent from the spec,
    while requires_review was incorrectly hardcoded to False."""

    # Trimmed from the real "Contact to CSV - Inst" transform.map component:
    # direct passthroughs, a Scripting function (FirstName+LastName -> fullname),
    # and a CrossRefLookup function (AccountId -> CompanyName via a ref table).
    MAP_COMPONENT_XML = """
    <bns:Component xmlns:bns="http://api.platform.boomi.com/" componentId="map-1" type="transform.map">
      <bns:object>
        <Map xmlns="" fromProfile="src-profile" toProfile="dst-profile">
          <Mappings>
            <Mapping fromKey="35" fromNamePath="Contact/CreatedDate" fromType="profile"
                     toKey="4" toNamePath="Record/Elements/CreateDate" toType="profile"/>
            <Mapping fromKey="7" fromNamePath="Contact/FirstName" fromType="profile"
                     toFunction="1" toKey="1" toType="function"/>
            <Mapping fromKey="6" fromNamePath="Contact/LastName" fromType="profile"
                     toFunction="1" toKey="2" toType="function"/>
            <Mapping fromFunction="1" fromKey="4" fromType="function"
                     toKey="3" toNamePath="Record/Elements/ContactName" toType="profile"/>
            <Mapping fromKey="5" fromNamePath="Contact/AccountId" fromType="profile"
                     toFunction="3" toKey="1" toType="function"/>
            <Mapping fromFunction="3" fromKey="2" fromType="function"
                     toKey="7" toNamePath="Record/Elements/CompanyName" toType="profile"/>
          </Mappings>
          <Functions>
            <FunctionStep category="Scripting" key="1" name="Scripting" type="Scripting">
              <Inputs><Input key="1" name="firstname"/><Input key="2" name="lastname"/></Inputs>
              <Outputs><Output key="4" name="fullname"/></Outputs>
              <Configuration><Scripting language="javascript">
                <ScriptToExecute>fullname = firstname + '||' + lastname;</ScriptToExecute>
              </Scripting></Configuration>
            </FunctionStep>
            <FunctionStep category="Lookup" key="3" name="Cross Reference Lookup" type="CrossRefLookup">
              <Inputs><Input key="1" name="Account ID"/></Inputs>
              <Outputs><Output key="2" name="Account Name"/></Outputs>
              <Configuration><CrossRefLookup crossRefTableId="734e6956-7ddb-4fe0-aca0-4b4b4c1bfd2a"/></Configuration>
            </FunctionStep>
          </Functions>
        </Map>
      </bns:object>
    </bns:Component>
    """

    # Trimmed from the real "Contact File - New" transform.map: a userdefined
    # Custom Function whose logic lives in a separate, NOT locally-pulled,
    # customfunction component (only its id is referenced here).
    MAP_WITH_UNRESOLVED_CUSTOM_FUNCTION_XML = """
    <bns:Component xmlns:bns="http://api.platform.boomi.com/" componentId="map-2" type="transform.map">
      <bns:object>
        <Map xmlns="" fromProfile="src-profile" toProfile="dst-profile">
          <Mappings>
            <Mapping fromKey="2" fromNamePath="Contact/OtherStreet" fromType="profile"
                     toFunction="3" toKey="2" toType="function"/>
            <Mapping fromFunction="3" fromKey="1" fromType="function"
                     toKey="1" toNamePath="Record/Elements/OtherStreet" toType="profile"/>
          </Mappings>
          <Functions>
            <FunctionStep category="userdefined" id="57939710-1087-4880-bcf8-12d738a1de35" key="3"
                          name="Remove Address Returns" type="userdefined">
              <Inputs><Input key="2" name="Street"/></Inputs>
              <Outputs><Output key="1" name="Street"/></Outputs>
              <Configuration/>
            </FunctionStep>
          </Functions>
        </Map>
      </bns:object>
    </bns:Component>
    """

    def _find_map_elem(self, component_xml):
        root = ET.fromstring(component_xml)
        return ab.find_elem(root, "Map")

    def test_direct_profile_to_profile_mapping_is_passthrough(self):
        field_mappings, unresolved, fully_resolved = ab._parse_map_component(
            self._find_map_elem(self.MAP_COMPONENT_XML), {}
        )
        direct = next(fm for fm in field_mappings if fm["target"] == "Record/Elements/CreateDate")
        self.assertEqual(direct["source"], "Contact/CreatedDate")
        self.assertEqual(direct["transformation"], "passthrough")
        self.assertTrue(fully_resolved)

    def test_scripting_function_resolves_real_javascript_logic(self):
        field_mappings, _, fully_resolved = ab._parse_map_component(
            self._find_map_elem(self.MAP_COMPONENT_XML), {}
        )
        scripted = next(fm for fm in field_mappings if fm["target"] == "Record/Elements/ContactName")
        self.assertEqual(scripted["transformation"], "custom")
        self.assertIn("Contact/FirstName", scripted["source"])
        self.assertIn("Contact/LastName", scripted["source"])
        self.assertIn("fullname = firstname + '||' + lastname;", scripted["expression"])
        self.assertTrue(fully_resolved)

    def test_cross_ref_lookup_function_resolves_to_readable_mapping(self):
        field_mappings, _, _ = ab._parse_map_component(
            self._find_map_elem(self.MAP_COMPONENT_XML), {}
        )
        looked_up = next(fm for fm in field_mappings if fm["target"] == "Record/Elements/CompanyName")
        self.assertEqual(looked_up["source"], "Contact/AccountId")
        self.assertEqual(looked_up["transformation"], "custom")
        self.assertIn("734e6956-7ddb-4fe0-aca0-4b4b4c1bfd2a", looked_up["expression"])

    def test_unresolved_custom_function_flags_fully_resolved_false(self):
        """A userdefined Custom Function whose component wasn't pulled locally
        must not silently present its field as a clean, trustworthy mapping."""
        field_mappings, _, fully_resolved = ab._parse_map_component(
            self._find_map_elem(self.MAP_WITH_UNRESOLVED_CUSTOM_FUNCTION_XML), {}
        )
        self.assertFalse(fully_resolved)
        mapped = next(fm for fm in field_mappings if fm["target"] == "Record/Elements/OtherStreet")
        self.assertIn("NOT found in local pull", mapped["expression"])

    def test_extract_map_step_requires_review_false_when_fully_resolved(self):
        shape = shape_from_xml(
            '<shape name="s1" shapetype="map"><configuration><map mapId="map-1"/></configuration>'
            "<dragpoints/></shape>"
        )
        component_index = {"map-1": (None, ET.ElementTree(ET.fromstring(self.MAP_COMPONENT_XML)))}
        step = ab.extract_map_step(shape, 1, component_index)
        self.assertFalse(step["requires_review"])
        self.assertGreaterEqual(len(step["field_mappings"]), 3)

    def test_extract_map_step_requires_review_true_when_component_missing(self):
        shape = shape_from_xml(
            '<shape name="s1" shapetype="map"><configuration><map mapId="does-not-exist"/></configuration>'
            "<dragpoints/></shape>"
        )
        step = ab.extract_map_step(shape, 1, {})
        self.assertTrue(step["requires_review"])
        self.assertEqual(step["field_mappings"], [])

    def test_extract_map_step_requires_review_true_when_custom_function_unresolved(self):
        shape = shape_from_xml(
            '<shape name="s1" shapetype="map"><configuration><map mapId="map-2"/></configuration>'
            "<dragpoints/></shape>"
        )
        component_index = {"map-2": (None, ET.ElementTree(ET.fromstring(self.MAP_WITH_UNRESOLVED_CUSTOM_FUNCTION_XML)))}
        step = ab.extract_map_step(shape, 1, component_index)
        self.assertTrue(step["requires_review"], "Partial data must not present itself as fully trustworthy")
        self.assertTrue(step["field_mappings"])  # the resolved fields are still kept, not thrown away


class TestStopShapeAndUnsupportedFallback(unittest.TestCase):
    """Boomi's <stop continue=".../"> carries real semantic meaning
    (soft path-end vs hard process-exit) that was previously collapsed into
    one identical silent break regardless of the attribute's value."""

    def test_stop_continue_true_is_silent_same_as_before(self):
        process_xml = """
        <shape name="start" shapetype="start"><configuration/>
          <dragpoints><dragpoint toShape="s1"/></dragpoints></shape>
        <shape name="s1" shapetype="stop">
          <configuration><stop continue="true"/></configuration><dragpoints/></shape>
        """
        steps, _ = traverse_from_process_xml(process_xml)
        self.assertEqual(steps, [])

    def test_stop_continue_false_emits_explicit_halt_step(self):
        process_xml = """
        <shape name="start" shapetype="start"><configuration/>
          <dragpoints><dragpoint toShape="s1"/></dragpoints></shape>
        <shape name="s1" shapetype="stop">
          <configuration><stop continue="false"/></configuration><dragpoints/></shape>
        """
        steps, _ = traverse_from_process_xml(process_xml)
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["type"], "halt_process")
        self.assertFalse(steps[0]["requires_review"])

    def test_returndocuments_is_flagged_not_silently_dropped(self):
        process_xml = """
        <shape name="start" shapetype="start"><configuration/>
          <dragpoints><dragpoint toShape="s1"/></dragpoints></shape>
        <shape name="s1" shapetype="returndocuments"><configuration/><dragpoints/></shape>
        """
        steps, _ = traverse_from_process_xml(process_xml)
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["type"], "unsupported_shape")
        self.assertTrue(steps[0]["requires_review"])

    def test_unrecognized_shape_type_produces_loud_stub_not_none(self):
        """Any shape type with no explicit branch in _classify_and_extract_shape
        must come back as a visible, requires_review stub -- never a silent
        None that the caller drops on the floor."""
        shape = shape_from_xml(
            '<shape name="s1" shapetype="some_future_boomi_shape_type">'
            "<configuration/><dragpoints/></shape>"
        )
        step, seq = ab._classify_and_extract_shape(shape, {}, set(), 0)
        self.assertIsNotNone(step)
        self.assertEqual(step["type"], "unsupported_shape")
        self.assertTrue(step["requires_review"])
        self.assertEqual(seq, 1)


if __name__ == "__main__":
    unittest.main()
