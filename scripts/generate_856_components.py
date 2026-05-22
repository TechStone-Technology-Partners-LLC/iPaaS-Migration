#!/usr/bin/env python3
"""
Generator for BWW_EDI_ShipNotice_In migration EDI/Map components.
Produces:
  - 1 canonical XML profile (target)
  - 3 EDI source profiles: X12, UCS, VICS 856
  - 7 Map components (one per standard/version)
All go into active-development/ subdirectories.
"""
import os, textwrap

FOLDER_ID = "Rjo4NTY2Mjcy"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, '..', 'active-development')

def ensure(d): os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# XML profile helpers
# ---------------------------------------------------------------------------

def xml_elem(key, name, mappable, max_occurs=1, min_occurs=0, children=''):
    im = 'true' if mappable else 'false'
    mo = str(max_occurs)
    el = (f'<XMLElement dataType="character" isMappable="{im}" isNode="true" '
          f'key="{key}" maxOccurs="{mo}" minOccurs="{min_occurs}" name="{name}" useNamespace="-1">\n'
          f'  <DataFormat><ProfileCharacterFormat/></DataFormat>\n')
    if children:
        # indent children by 2 extra spaces
        for line in children.splitlines(True):
            el += '  ' + line
    el += f'</XMLElement>\n'
    return el

def e(key, name, mo=1, mi=0):
    return xml_elem(key, name, True, mo, mi)

def c(key, name, mo=1, mi=0, children=''):
    return xml_elem(key, name, False, mo, mi, children)

# ---------------------------------------------------------------------------
# EDI profile helpers
# ---------------------------------------------------------------------------

def ef(key, name, mandatory=False, dt='AN', minL=1, maxL=50, autoGen='na'):
    m = 'true' if mandatory else 'false'
    return (f'<EdiDataElement key="{key}" name="{name}" dataType="{dt}" '
            f'mandatory="{m}" minLength="{minL}" maxLength="{maxL}"'
            f' isMappable="true" isNode="true" autoGenOption="{autoGen}">\n'
            f'  <DataFormat><ProfileCharacterFormat/></DataFormat>\n'
            f'</EdiDataElement>\n')

def seg(key, sname, seg_id, pos, mandatory=False, loop_opt='unique', max_use=1,
        use_add=False, add_key=None, add_name=None, add_val=None, children=''):
    m = 'true' if mandatory else 'false'
    add = ''
    if use_add:
        add = (f' useAdditionalCriteria="true" additionalElementKey="{add_key}"'
               f' additionalElementName="{add_name}" additionalElementValue="{add_val}"')
    result = (f'<EdiSegment key="{key}" name="{seg_id}" segmentName="{sname}" '
              f'position="{pos}" mandatory="{m}" maxUse="{max_use}" '
              f'loopingOption="{loop_opt}" isNode="true"{add}>\n')
    for line in children.splitlines(True):
        result += '  ' + line
    result += f'</EdiSegment>\n'
    return result

def loop_elem(key, name, loop_id, repeat, loop_opt, is_container=False, children=''):
    ic = ' isContainer="true"' if is_container else ''
    result = (f'<EdiLoop key="{key}" name="{name}" loopId="{loop_id}" '
              f'loopRepeat="{repeat}" loopingOption="{loop_opt}" isNode="true"{ic}>\n')
    for line in children.splitlines(True):
        result += '  ' + line
    result += f'</EdiLoop>\n'
    return result

def wrap_component(name, ctype, desc, obj_content, cid='', subtype=''):
    st = f'\n               subType="{subtype}"' if subtype else ''
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<bns:Component xmlns:bns="http://api.platform.boomi.com/"\n'
            f'               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            f'               componentId="{cid}" name="{name}"\n'
            f'               type="{ctype}"{st}\n'
            f'               folderId="{FOLDER_ID}">\n'
            f'  <bns:encryptedValues/>\n'
            f'  <bns:description>{desc}</bns:description>\n'
            f'  <bns:object>\n'
            f'{obj_content}\n'
            f'  </bns:object>\n'
            f'</bns:Component>\n')

# ---------------------------------------------------------------------------
# 1. Canonical XML Profile
# ---------------------------------------------------------------------------

def build_canonical_xml_profile():
    sub_item = (
        e(106, 'QuantityShipped') + e(107, 'UOMCode') +
        c(108, 'ProductServiceIdentifier', children=(
            e(109, 'ProductServiceIdQualifier') + e(110, 'ProductServiceId')
        ))
    )
    item_detail = (
        e(86, 'HierarchLevelCode') + e(87, 'QuantityShipped') + e(88, 'UOMCode') +
        e(89, 'Description') + e(90, 'AssignedNumber') +
        c(91, 'PhysicalDetail', children=(
            e(92, 'Pack') + e(93, 'Size') +
            e(94, 'UnitBasisOfMeasurementCode') + e(95, 'InnerPack')
        )) +
        c(96, 'ProductServiceIdentifier', mo=-1, children=(
            e(97, 'ProductServiceIdQualifier') + e(98, 'ProductServiceId')
        )) +
        c(99, 'DateTime', mo=-1, children=(
            e(100, 'DateTimeQualifier') + e(101, 'DateTimeValue')
        )) +
        c(102, 'Reference', mo=-1, children=(
            e(103, 'ReferenceQualifier') + e(104, 'ReferenceValue')
        )) +
        c(105, 'SubItemDetail', mo=-1, children=sub_item)
    )
    pack_detail = (
        e(66, 'HierarchLevelCode') + e(67, 'QuantityShipped') + e(68, 'UOMCode') +
        e(69, 'Description') + e(70, 'AssignedNumber') +
        c(71, 'PhysicalDetail', children=(
            e(72, 'Pack') + e(73, 'Size') +
            e(74, 'UnitBasisOfMeasurementCode') + e(75, 'InnerPack')
        )) +
        c(76, 'ProductServiceIdentifier', mo=-1, children=(
            e(77, 'ProductServiceIdQualifier') + e(78, 'ProductServiceId')
        )) +
        c(79, 'DateTime', mo=-1, children=(
            e(80, 'DateTimeQualifier') + e(81, 'DateTimeValue')
        )) +
        c(82, 'Reference', mo=-1, children=(
            e(83, 'ReferenceQualifier') + e(84, 'ReferenceValue')
        )) +
        c(85, 'ItemDetail', mo=-1, children=item_detail)
    )
    tare_detail = (
        e(58, 'PalletTypeCode') + e(59, 'PalletTiers') +
        e(60, 'PalletBlocks') + e(61, 'PalletPack') +
        c(62, 'MarksAndNumbers', mo=-1, children=(e(63, 'Qualifier') + e(64, 'Marks'))) +
        c(65, 'PackDetail', children=pack_detail)
    )
    order_detail = (
        e(52, 'PurchaseOrderNumber') + e(53, 'PurchaseOrderDate') +
        c(54, 'Reference', mo=-1, children=(
            e(55, 'ReferenceQualifier') + e(56, 'ReferenceValue')
        )) +
        c(57, 'TareDetail', mo=-1, children=tare_detail)
    )
    shipment_detail = (
        c(11, 'Partner', mo=-1, children=(
            e(12, 'PartnerType') + e(13, 'PartnerNumber') +
            c(14, 'Address', children=(
                e(15, 'Name1') + e(16, 'Street1') + e(17, 'Street2') +
                e(18, 'City') + e(19, 'State') +
                e(20, 'PostalCode') + e(21, 'CountryCode')
            )) +
            c(22, 'Contact', children=(
                e(23, 'ContactId') + e(24, 'ContactType') +
                e(25, 'Phone') + e(26, 'Fax') + e(27, 'Email')
            ))
        )) +
        c(28, 'QuantityAndWeight', children=(
            e(29, 'PackagingCode') + e(30, 'LadingQuantity') +
            e(31, 'WeightQualifier') + e(32, 'Weight') + e(33, 'WeightUOM')
        )) +
        c(34, 'TransportationRouting', children=(
            e(35, 'RoutingSequenceCode') + e(36, 'Routing') +
            e(37, 'TransportTypeCode') + e(38, 'ShipOrderStatusCode') +
            e(39, 'SCAC') + e(40, 'ShipMethodOfPayment') +
            e(41, 'PalletShipQuantity') + e(42, 'PalletExchangeCode')
        )) +
        c(43, 'Reference', mo=-1, children=(
            e(44, 'ReferenceQualifier') + e(45, 'ReferenceValue')
        )) +
        c(46, 'DateTime', mo=-1, children=(
            e(47, 'DateTimeQualifier') + e(48, 'DateTimeValue')
        )) +
        e(49, 'ShipmentDateTime') + e(50, 'ScheduledDeliveryDate') +
        c(51, 'OrderDetail', mo=-1, children=order_detail)
    )
    data_elements = c(1, 'ShipNotice', children=(
        c(2, 'ControlArea', children=e(3, 'SenderId')) +
        c(4, 'DataArea', children=(
            c(5, 'Header', children=(
                e(6, 'DocumentDateTime') + e(7, 'TransactionSetPurposeCode') +
                e(8, 'ShipmentIdentification') + e(9, 'HierarchicalStructureCode')
            )) +
            c(10, 'ShipmentDetail', mo=-1, children=shipment_detail)
        ))
    ))

    obj = ('    <XMLProfile modelVersion="2" strict="true">\n'
           '      <ProfileProperties>\n'
           '        <XMLGeneralInfo/>\n'
           '        <XMLOptions encoding="utf8" implicitElementOrdering="true" parseRespectMaxOccurs="true">\n'
           '          <XMLFlavor><CustomStandardFlavor/></XMLFlavor>\n'
           '        </XMLOptions>\n'
           '      </ProfileProperties>\n'
           '      <DataElements>\n')
    for line in data_elements.splitlines(True):
        obj += '        ' + line
    obj += ('      </DataElements>\n'
            '      <Namespaces/>\n'
            '    </XMLProfile>')
    return wrap_component(
        'MIG_WM_ShipNotice_Canonical_Profile', 'profile.xml',
        'Canonical ShipNotice XML target profile for all 7 BWW_EDI_ShipNotice_In 856 map components. '
        'Represents BWW_Canonical.ShipNotice:ShipNotice. Keys 1-110. '
        '| migrated from BWW_EDI_ShipNotice_In webMethods package',
        obj)

# ---------------------------------------------------------------------------
# 2. EDI Profile builder
# ---------------------------------------------------------------------------

def build_edi_profile(standard, std_version, include_fob=True):
    name_map = {'x12': 'X12', 'ucs': 'UCS', 'vics': 'VICS'}
    std_upper = name_map.get(standard, standard.upper())
    comp_name = f'MIG_WM_856_{std_upper}_Profile'

    # Key offsets: FOB occupies keys 50-51 in X12; omitted in UCS/VICS
    fob_offset = 2 if include_fob else 0
    pal_s  = 50 + fob_offset
    ref_s  = pal_s + 3
    dtm_s  = ref_s + 3
    hlo    = dtm_s + 3  # HL_O loop key
    prf    = hlo + 6
    ref_o  = prf + 3
    hlp    = ref_o + 3  # HL_P loop key
    man    = hlp + 5
    pal_p  = man + 3
    hli    = pal_p + 5  # HL_I loop key
    lin    = hli + 5
    sn1    = lin + 10
    pid    = sn1 + 4
    po4    = pid + 3
    sln    = po4 + 5
    dtm_i  = sln + 8
    ref_i  = dtm_i + 3
    se     = ref_i + 3

    # --- Header ---
    header = (
        seg(4, 'Transaction Set Header', 'ST', '010', mandatory=True, children=
            ef(5, 'ST01', dt='ID', minL=3, maxL=3) + ef(6, 'ST02', dt='AN', minL=4, maxL=9)) +
        seg(7, 'Beginning Segment for Ship Notice', 'BSN', '020', mandatory=True, children=
            ef(8,  'BSN01', dt='ID', minL=2, maxL=2) +
            ef(9,  'BSN02', dt='AN', minL=2, maxL=30) +
            ef(10, 'BSN03', dt='DT', minL=8, maxL=8) +
            ef(11, 'BSN04', dt='TM', minL=4, maxL=8) +
            ef(12, 'BSN05', dt='ID', minL=2, maxL=2))
    )

    # --- N1 loop ---
    n1_loop = loop_elem(19, 'N1_Loop', 'N1', 10, 'occurrence', children=
        seg(20, 'Name', 'N1', '010', mandatory=True, loop_opt='occurrence', children=
            ef(21, 'N101', dt='ID', minL=2, maxL=3) +
            ef(22, 'N102', dt='AN', minL=1, maxL=60) +
            ef(23, 'N104', dt='AN', minL=1, maxL=80)) +
        seg(24, 'Address Information', 'N3', '020', loop_opt='occurrence', children=
            ef(25, 'N301', dt='AN', minL=1, maxL=55) +
            ef(26, 'N302', dt='AN', minL=1, maxL=55)) +
        seg(27, 'Geographic Location', 'N4', '030', loop_opt='occurrence', children=
            ef(28, 'N401', dt='AN', minL=2, maxL=30) +
            ef(29, 'N402', dt='ID', minL=2, maxL=2) +
            ef(30, 'N403', dt='ID', minL=3, maxL=15) +
            ef(31, 'N404', dt='ID', minL=2, maxL=3)) +
        seg(32, 'Administrative Communications Contact', 'PER', '040', loop_opt='occurrence', children=
            ef(33, 'PER01', dt='ID', minL=2, maxL=2) +
            ef(34, 'PER02', dt='AN', minL=1, maxL=60) +
            ef(35, 'PER04', dt='AN', minL=1, maxL=80) +
            ef(36, 'PER06', dt='AN', minL=1, maxL=80) +
            ef(37, 'PER08', dt='AN', minL=1, maxL=80))
    )

    td1 = seg(38, 'Carrier Details Qty and Weight', 'TD1', '050', children=
        ef(39, 'TD101', dt='AN', minL=3, maxL=5) + ef(40, 'TD102', dt='N0', minL=1, maxL=7) +
        ef(41, 'TD106', dt='ID', minL=1, maxL=2) + ef(42, 'TD107', dt='R', minL=1, maxL=10) +
        ef(43, 'TD108', dt='ID', minL=2, maxL=2))
    td5 = seg(44, 'Carrier Details Routing Sequence', 'TD5', '060', children=
        ef(45, 'TD501', dt='ID', minL=1, maxL=2) + ef(46, 'TD503', dt='AN', minL=2, maxL=4) +
        ef(47, 'TD504', dt='ID', minL=1, maxL=2) + ef(48, 'TD505', dt='AN', minL=1, maxL=35) +
        ef(49, 'TD506', dt='ID', minL=1, maxL=2))

    fob_seg = ''
    if include_fob:
        fob_seg = seg(50, 'Free On Board', 'FOB', '065', children=
            ef(51, 'FOB01', dt='ID', minL=1, maxL=2))

    pal_s_seg = seg(pal_s, 'Pallet Type and Characteristics (S)', 'PAL', '070', children=
        ef(pal_s+1, 'PAL04', dt='R',  minL=1, maxL=10) +
        ef(pal_s+2, 'PAL15', dt='ID', minL=1, maxL=2))
    ref_s_seg = seg(ref_s, 'Reference Identification (S)', 'REF', '080',
        loop_opt='occurrence', max_use=-1, children=
        ef(ref_s+1, 'REF01', dt='ID', minL=2, maxL=3) +
        ef(ref_s+2, 'REF02', dt='AN', minL=1, maxL=80))
    dtm_s_seg = seg(dtm_s, 'Date/Time Reference (S)', 'DTM', '090',
        loop_opt='occurrence', max_use=-1, children=
        ef(dtm_s+1, 'DTM01', dt='ID', minL=3, maxL=3) +
        ef(dtm_s+2, 'DTM02', dt='DT', minL=8, maxL=8))

    # HL_O
    prf_seg = seg(prf, 'Purchase Order Reference', 'PRF', '030', children=
        ef(prf+1, 'PRF01', dt='AN', minL=1, maxL=22) +
        ef(prf+2, 'PRF04', dt='DT', minL=8, maxL=8))
    ref_o_seg = seg(ref_o, 'Reference Identification (O)', 'REF', '040',
        loop_opt='occurrence', max_use=-1, children=
        ef(ref_o+1, 'REF01', dt='ID', minL=2, maxL=3) +
        ef(ref_o+2, 'REF02', dt='AN', minL=1, maxL=80))

    # HL_P
    man_seg = seg(man, 'Marks and Numbers', 'MAN', '030',
        loop_opt='occurrence', max_use=-1, children=
        ef(man+1, 'MAN01', dt='ID', minL=1, maxL=2) +
        ef(man+2, 'MAN02', dt='AN', minL=1, maxL=48))
    pal_p_seg = seg(pal_p, 'Pallet Type and Characteristics (P)', 'PAL', '040', children=
        ef(pal_p+1, 'PAL01', dt='ID', minL=1, maxL=2) +
        ef(pal_p+2, 'PAL03', dt='N0', minL=1, maxL=3) +
        ef(pal_p+3, 'PAL04', dt='N0', minL=1, maxL=3) +
        ef(pal_p+4, 'PAL05', dt='N0', minL=1, maxL=3))

    # HL_I
    lin_seg = seg(lin, 'Item Identification', 'LIN', '010', children=
        ef(lin+1, 'LIN01', dt='AN', minL=1, maxL=20) +
        ef(lin+2, 'LIN02', dt='ID', minL=2, maxL=2) + ef(lin+3, 'LIN03', dt='AN', minL=1, maxL=30) +
        ef(lin+4, 'LIN04', dt='ID', minL=2, maxL=2) + ef(lin+5, 'LIN05', dt='AN', minL=1, maxL=30) +
        ef(lin+6, 'LIN06', dt='ID', minL=2, maxL=2) + ef(lin+7, 'LIN07', dt='AN', minL=1, maxL=30) +
        ef(lin+8, 'LIN08', dt='ID', minL=2, maxL=2) + ef(lin+9, 'LIN09', dt='AN', minL=1, maxL=30))
    sn1_seg = seg(sn1, 'Item Detail Shipment', 'SN1', '020', children=
        ef(sn1+1, 'SN101', dt='AN', minL=1, maxL=20) +
        ef(sn1+2, 'SN102', dt='R',  minL=1, maxL=10) +
        ef(sn1+3, 'SN103', dt='ID', minL=2, maxL=2))
    pid_seg = seg(pid, 'Product/Item Description', 'PID', '030', children=
        ef(pid+1, 'PID01', dt='ID', minL=1, maxL=1) +
        ef(pid+2, 'PID05', dt='AN', minL=1, maxL=80))
    po4_seg = seg(po4, 'Item Physical Details', 'PO4', '040', children=
        ef(po4+1, 'PO401', dt='N0', minL=1, maxL=6) + ef(po4+2, 'PO402', dt='R', minL=1, maxL=8) +
        ef(po4+3, 'PO403', dt='ID', minL=2, maxL=2) + ef(po4+4, 'PO414', dt='N0', minL=1, maxL=6))
    sln_seg = seg(sln, 'Subline Item Detail', 'SLN', '050',
        loop_opt='occurrence', max_use=-1, children=
        ef(sln+1, 'SLN01', dt='AN', minL=1, maxL=6) + ef(sln+2, 'SLN02', dt='AN', minL=1, maxL=6) +
        ef(sln+3, 'SLN03', dt='ID', minL=1, maxL=1) + ef(sln+4, 'SLN04', dt='R',  minL=1, maxL=10) +
        ef(sln+5, 'SLN05', dt='ID', minL=2, maxL=2) +
        ef(sln+6, 'SLN09', dt='ID', minL=2, maxL=2) + ef(sln+7, 'SLN10', dt='AN', minL=1, maxL=30))
    dtm_i_seg = seg(dtm_i, 'Date/Time Reference (I)', 'DTM', '060',
        loop_opt='occurrence', max_use=-1, children=
        ef(dtm_i+1, 'DTM01', dt='ID', minL=3, maxL=3) +
        ef(dtm_i+2, 'DTM02', dt='DT', minL=8, maxL=8))
    ref_i_seg = seg(ref_i, 'Reference Identification (I)', 'REF', '070',
        loop_opt='occurrence', max_use=-1, children=
        ef(ref_i+1, 'REF01', dt='ID', minL=2, maxL=3) +
        ef(ref_i+2, 'REF02', dt='AN', minL=1, maxL=80))

    # Assemble HL loops (nested)
    hli_loop = loop_elem(hli, 'HL_I', 'I', 200000, 'occurrence', children=
        seg(hli+1, 'Hierarchical Level', 'HL', '010', mandatory=True,
            use_add=True, add_key=hli+4, add_name='HL03', add_val='I', children=
            ef(hli+2, 'HL01', dt='AN', minL=1, maxL=12, autoGen='hierarc1') +
            ef(hli+3, 'HL02', dt='AN', minL=1, maxL=12, autoGen='hierarc2') +
            ef(hli+4, 'HL03', dt='ID', minL=1, maxL=2) +
            ef(hli+5, 'HL04', dt='ID', minL=1, maxL=1)) +
        lin_seg + sn1_seg + pid_seg + po4_seg + sln_seg + dtm_i_seg + ref_i_seg)

    hlp_loop = loop_elem(hlp, 'HL_P', 'P', 200000, 'occurrence', children=
        seg(hlp+1, 'Hierarchical Level', 'HL', '010', mandatory=True,
            use_add=True, add_key=hlp+4, add_name='HL03', add_val='P', children=
            ef(hlp+2, 'HL01', dt='AN', minL=1, maxL=12, autoGen='hierarc1') +
            ef(hlp+3, 'HL02', dt='AN', minL=1, maxL=12, autoGen='hierarc2') +
            ef(hlp+4, 'HL03', dt='ID', minL=1, maxL=2) +
            ef(hlp+5, 'HL04', dt='ID', minL=1, maxL=1)) +
        man_seg + pal_p_seg + hli_loop)

    hlo_loop = loop_elem(hlo, 'HL_O', 'O', 200000, 'occurrence', children=
        seg(hlo+1, 'Hierarchical Level', 'HL', '010', mandatory=True,
            use_add=True, add_key=hlo+4, add_name='HL03', add_val='O', children=
            ef(hlo+2, 'HL01', dt='AN', minL=1, maxL=12, autoGen='hierarc1') +
            ef(hlo+3, 'HL02', dt='AN', minL=1, maxL=12, autoGen='hierarc2') +
            ef(hlo+4, 'HL03', dt='ID', minL=1, maxL=2) +
            ef(hlo+5, 'HL04', dt='ID', minL=1, maxL=1)) +
        prf_seg + ref_o_seg + hlp_loop)

    hls_loop = loop_elem(13, 'HL_S', 'S', 200000, 'occurrence', children=
        seg(14, 'Hierarchical Level', 'HL', '010', mandatory=True,
            use_add=True, add_key=17, add_name='HL03', add_val='S', children=
            ef(15, 'HL01', dt='AN', minL=1, maxL=12, autoGen='hierarc1') +
            ef(16, 'HL02', dt='AN', minL=1, maxL=12, autoGen='hierarc2') +
            ef(17, 'HL03', dt='ID', minL=1, maxL=2) +
            ef(18, 'HL04', dt='ID', minL=1, maxL=1)) +
        n1_loop + td1 + td5 + fob_seg + pal_s_seg + ref_s_seg + dtm_s_seg + hlo_loop)

    summary = seg(se, 'Transaction Set Trailer', 'SE', '010', mandatory=True, children=
        ef(se+1, 'SE01', dt='N0', minL=1, maxL=10) +
        ef(se+2, 'SE02', dt='AN', minL=4, maxL=9))

    # UCS and VICS are X12 variants — Boomi uses EdiX12Options for all three
    std_opt_map = {
        'x12':  f'<EdiX12Options isacontrolstandard="U" isacontrolversion="00401" stdversion="{std_version}" tranfuncid="SH" transmission="856"/>',
        'ucs':  f'<EdiX12Options isacontrolstandard="U" isacontrolversion="00401" stdversion="{std_version}" tranfuncid="SH" transmission="856"/>',
        'vics': f'<EdiX12Options isacontrolstandard="U" isacontrolversion="00401" stdversion="{std_version}" tranfuncid="SH" transmission="856"/>',
    }

    header_loop  = loop_elem(1, 'Header',  '1', 1,  'unique', is_container=True, children=header)
    detail_loop  = loop_elem(2, 'Detail',  '2', -1, 'unique', is_container=True, children=hls_loop)
    summary_loop = loop_elem(3, 'Summary', '3', 1,  'unique', is_container=True, children=summary)

    data_elements = header_loop + detail_loop + summary_loop

    obj = ('    <EdiProfile strict="true">\n'
           '      <ProfileProperties>\n'
           f'        <EdiGeneralInfo conditionalValidationEnabled="true" standard="{standard}"/>\n'
           '        <EdiFileOptions fileType="delimited">\n'
           '          <EdiDelimitedOptions fileDelimiter="stardelimited" repeatDelimiter="tildedelimited" segmentchar="tilde"/>\n'
           '          <EdiDataOptions/>\n'
           '        </EdiFileOptions>\n'
           '        <EdiOptions>\n'
           f'          {std_opt_map.get(standard, "")}\n'
           '        </EdiOptions>\n'
           '      </ProfileProperties>\n'
           '      <DataElements>\n')
    for line in data_elements.splitlines(True):
        obj += '        ' + line
    obj += ('      </DataElements>\n'
            '    </EdiProfile>')

    fob_note = ' Includes FOB.' if include_fob else ' No FOB.'
    desc = (f'{std_upper} 856 ASN EDI source profile.{fob_note} '
            f'Segments: BSN, HL(S/O/P/I), N1/N3/N4/PER, TD1, TD5, PAL, REF, DTM, PRF, MAN, LIN, SN1, PID, PO4, SLN. '
            f'| migrated from BWW_EDI_ShipNotice_In - EDIFFSchema.{std_upper}.V{std_version}:T856DT')

    return wrap_component(comp_name, 'profile.edi', desc, obj)

# ---------------------------------------------------------------------------
# 3. Map Components
# ---------------------------------------------------------------------------

def build_map(standard, version, xml_pid, edi_pid, include_fob=True):
    name_map = {'x12': 'X12', 'ucs': 'UCS', 'vics': 'VICS'}
    std_upper = name_map.get(standard, standard.upper())
    comp_name = f'MIG_WM_Map_856_{std_upper}_{version}_to_Canonical'

    fob_offset = 2 if include_fob else 0
    pal_s = 50 + fob_offset
    ref_s = pal_s + 3
    dtm_s = ref_s + 3
    hlo   = dtm_s + 3
    prf   = hlo + 6
    ref_o = prf + 3
    hlp   = ref_o + 3
    man   = hlp + 5
    pal_p = man + 3
    hli   = pal_p + 5
    lin   = hli + 5
    sn1   = lin + 10
    pid   = sn1 + 4
    po4   = pid + 3
    sln   = po4 + 5

    def m(fk, tk):
        return f'        <Mapping fromKey="{fk}" fromType="profile" toKey="{tk}" toType="profile"/>\n'

    fob_m = m(51, 40) if include_fob else ''  # FOB01 -> ShipMethodOfPayment

    # BSN03+BSN04 -> DocumentDateTime via Groovy function (key 1)
    fn_mappings = (
        '        <!-- BSN03+BSN04 -> DocumentDateTime via ConcatDateTime function -->\n'
        '        <Mapping fromKey="10" fromType="profile" toFunction="1" toKey="1" toType="function"/>\n'
        '        <Mapping fromKey="11" fromType="profile" toFunction="1" toKey="2" toType="function"/>\n'
        '        <Mapping fromFunction="1" fromKey="3" fromType="function" toKey="6" toType="profile"/>\n'
    )

    mappings = (
        '        <!-- BSN header -->\n' +
        m(8,  7) + m(9,  8) + m(12, 9) +
        '        <!-- N1 loop -> Partner -->\n' +
        m(21, 12) + m(22, 15) + m(23, 13) +
        m(25, 16) + m(26, 17) +
        m(28, 18) + m(29, 19) + m(30, 20) + m(31, 21) +
        m(33, 24) + m(34, 23) + m(35, 25) + m(36, 26) + m(37, 27) +
        '        <!-- TD1 -> QuantityAndWeight -->\n' +
        m(39, 29) + m(40, 30) + m(41, 31) + m(42, 32) + m(43, 33) +
        '        <!-- TD5 -> TransportationRouting -->\n' +
        m(45, 35) + m(46, 39) + m(47, 37) + m(48, 36) + m(49, 38) +
        fob_m +
        '        <!-- PAL at S -> TransportationRouting -->\n' +
        m(pal_s+1, 41) + m(pal_s+2, 42) +
        '        <!-- REF at S -> Reference[] -->\n' +
        m(ref_s+1, 44) + m(ref_s+2, 45) +
        '        <!-- DTM at S -> DateTime[] -->\n' +
        m(dtm_s+1, 47) + m(dtm_s+2, 48) +
        '        <!-- PRF -> OrderDetail -->\n' +
        m(prf+1, 52) + m(prf+2, 53) +
        '        <!-- REF at O -> OrderDetail/Reference[] -->\n' +
        m(ref_o+1, 55) + m(ref_o+2, 56) +
        '        <!-- MAN -> MarksAndNumbers[] -->\n' +
        m(man+1, 63) + m(man+2, 64) +
        '        <!-- PAL at P -> TareDetail -->\n' +
        m(pal_p+1, 58) + m(pal_p+2, 59) + m(pal_p+3, 60) + m(pal_p+4, 61) +
        '        <!-- HL_P -> PackDetail (P-level SN1/PID/PO4/LIN) -->\n' +
        m(hlp+4, 66) +
        m(sn1+2, 67) + m(sn1+3, 68) +
        m(pid+2, 69) +
        m(po4+1, 72) + m(po4+2, 73) + m(po4+3, 74) + m(po4+4, 75) +
        m(lin+1, 70) + m(lin+2, 77) + m(lin+3, 78) +
        '        <!-- HL_I -> ItemDetail (I-level SN1/PID/PO4/LIN) -->\n' +
        m(hli+4, 86) +
        m(sn1+2, 87) + m(sn1+3, 88) +
        m(pid+2, 89) +
        m(po4+1, 92) + m(po4+2, 93) + m(po4+3, 94) + m(po4+4, 95) +
        m(lin+1, 90) + m(lin+2, 97) + m(lin+3, 98) +
        '        <!-- SLN -> SubItemDetail -->\n' +
        m(sln+4, 106) + m(sln+5, 107) + m(sln+6, 109) + m(sln+7, 110) +
        fn_mappings
    )

    # Groovy FunctionStep for DocumentDateTime: BSN03 + 'T' + BSN04
    groovy = (
        '      <FunctionStep cacheEnabled="true" category="Scripting" key="1"'
        ' name="ConcatDateTime" position="1" sumEnabled="false" type="Scripting"'
        ' x="10.0" y="10.0">\n'
        '        <Inputs>\n'
        '          <Input key="1" name="bsn03"/>\n'
        '          <Input key="2" name="bsn04"/>\n'
        '        </Inputs>\n'
        '        <Outputs>\n'
        '          <Output key="3" name="result"/>\n'
        '        </Outputs>\n'
        '        <Configuration>\n'
        '          <Scripting language="groovy2">\n'
        '            <ScriptToExecute><![CDATA[result = bsn03 + \'T\' + bsn04\n'
        'return [result]]]></ScriptToExecute>\n'
        '            <Input dataType="character" index="1" name="bsn03"/>\n'
        '            <Input dataType="character" index="2" name="bsn04"/>\n'
        '            <Output index="3" name="result"/>\n'
        '          </Scripting>\n'
        '        </Configuration>\n'
        '      </FunctionStep>\n'
    )

    obj = (
        f'    <Map fromProfile="{edi_pid}" toProfile="{xml_pid}">\n'
        f'      <Mappings>\n'
        f'{mappings}'
        f'      </Mappings>\n'
        f'      <Functions optimizeExecutionOrder="true">\n'
        f'{groovy}'
        f'      </Functions>\n'
        f'      <Defaults/>\n'
        f'      <DocumentCacheJoins/>\n'
        f'    </Map>'
    )

    desc = (
        f'Maps {std_upper} {version} 856 EDI to canonical ShipNotice XML. '
        f'SETUP REQUIRED: (1) Replace N101->PartnerType direct map with Cross Reference Table lookup. '
        f'(2) Add DTM qualifier routing for ShipmentDateTime/ScheduledDeliveryDate (instance identifiers). '
        f'(3) Verify DocumentDateTime Groovy concat (BSN03+T+BSN04). '
        f'| migrated from BWW_EDI_ShipNotice_In.EDI_Canonical.{std_upper}_{version}_856.map856ToCanonical'
    )

    return wrap_component(comp_name, 'transform.map', desc, obj)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# Placeholder profile IDs - will be replaced after profiles are pushed to platform
PLACEHOLDER_XML  = '59294e62-db5a-4412-82c5-1a63d6763adb'  # MIG_WM_ShipNotice_Canonical_Profile
PLACEHOLDER_X12  = 'd668ac70-5340-4456-8fa9-e7e28bb2ec7c'  # MIG_WM_856_X12_Profile
PLACEHOLDER_UCS  = '3e61a061-eb8e-462d-81b4-35802addd76d'  # MIG_WM_856_UCS_Profile
PLACEHOLDER_VICS = '90d25d21-89ef-40de-8528-2f25804b52e3'  # MIG_WM_856_VICS_Profile

def main():
    xml_dir = os.path.join(OUT_DIR, 'profile.xml')
    edi_dir = os.path.join(OUT_DIR, 'profile.edi')
    map_dir = os.path.join(OUT_DIR, 'transform.map')
    for d in [xml_dir, edi_dir, map_dir]:
        ensure(d)

    # Canonical XML profile
    path = os.path.join(xml_dir, 'MIG_WM_ShipNotice_Canonical_Profile.xml')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(build_canonical_xml_profile())
    print(f'[OK] {path}')

    # EDI source profiles (one per standard)
    for std, ver, fob in [('x12','4010',True), ('ucs','4010',False), ('vics','4010',False)]:
        nm = {'x12':'X12','ucs':'UCS','vics':'VICS'}[std]
        path = os.path.join(edi_dir, f'MIG_WM_856_{nm}_Profile.xml')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(build_edi_profile(std, ver, fob))
        print(f'[OK] {path}')

    # Map components (7 versions)
    for std, ver, edi_pid, fob in [
        ('x12','4010', PLACEHOLDER_X12,  True),
        ('x12','4030', PLACEHOLDER_X12,  True),
        ('x12','5010', PLACEHOLDER_X12,  True),
        ('ucs','4010', PLACEHOLDER_UCS,  False),
        ('ucs','4030', PLACEHOLDER_UCS,  False),
        ('ucs','5010', PLACEHOLDER_UCS,  False),
        ('vics','4010',PLACEHOLDER_VICS, False),
    ]:
        nm = {'x12':'X12','ucs':'UCS','vics':'VICS'}[std]
        path = os.path.join(map_dir, f'MIG_WM_Map_856_{nm}_{ver}_to_Canonical.xml')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(build_map(std, ver, PLACEHOLDER_XML, edi_pid, fob))
        print(f'[OK] {path}')

    print('\nDone. Push order: profiles first (XML then EDI), then maps.')
    print('After each profile push, update the PLACEHOLDER_* IDs in this script with real platform IDs.')

if __name__ == '__main__':
    main()
