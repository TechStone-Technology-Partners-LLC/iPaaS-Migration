# Boomi Map XML Patterns

Use these validated snippets when building map components.
The map component XML structure is the same regardless of profile types.

---

## Map component shell

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bns:Component xmlns:bns="http://api.platform.boomi.com/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               componentId="COMPONENT_ID"
               name="MY_MAP"
               type="transform.map"
               folderId="FOLDER_ID">
  <bns:encryptedValues/>
  <bns:description>DESCRIPTION</bns:description>
  <bns:object>
    <Map fromProfile="SOURCE_PROFILE_ID"
         toProfile="TARGET_PROFILE_ID">
      <Mappings>
        <!-- mapping elements go here -->
      </Mappings>
      <Functions optimizeExecutionOrder="true">
        <!-- function steps go here -->
      </Functions>
      <Defaults>
        <!-- default values go here -->
      </Defaults>
      <DocumentCacheJoins/>
    </Map>
  </bns:object>
</bns:Component>
```

---

## Pattern 1: Direct field copy (no transformation)

Maps source key N directly to target key M with no function involved.

```xml
<Mapping fromKey="3" fromType="profile"
         toKey="4" toType="profile"/>
```

---

## Pattern 2: Date format conversion

Two mapping lines plus one FunctionStep.
- Line 1: source field -> function input (toKey="1" = "Date String" input)
- Line 2: function output (fromKey="2" = "Result") -> target field
- The date format function output key is always "2" (not "1")

```xml
<!-- Mapping: source dateField (key=6) -> Date Format function 1 input -->
<Mapping fromKey="6" fromType="profile"
         toFunction="1" toKey="1" toType="function"/>

<!-- Mapping: Date Format function 1 output -> target dateField (key=7) -->
<Mapping fromFunction="1" fromKey="2" fromType="function"
         toKey="7" toType="profile"/>
```

```xml
<FunctionStep cacheEnabled="true" category="Date" key="1" name="Date Format"
              position="1" sumEnabled="false" type="DateFormat" x="10.0" y="10.0">
  <Inputs>
    <Input key="1" name="Date String"/>
    <Input key="2" name="Input Mask" default="MM/dd/yyyy"/>
    <Input key="3" name="Output Mask" default="yyyy-MM-dd"/>
  </Inputs>
  <Outputs>
    <Output key="2" name="Result"/>
  </Outputs>
  <Configuration/>
</FunctionStep>
```

**Note:** Update `default="MM/dd/yyyy"` (Input Mask) to match the actual incoming date format.
Common values: `MM/dd/yyyy`, `yyyy-MM-dd`, `yyyyMMdd`, `yyyy-MM-dd'T'HH:mm:ss`

---

## Pattern 3: Groovy scripting (value conversion)

Two mapping lines plus one FunctionStep with embedded Groovy.
- Input key = 1, Output key = 2 (convention for single-input/output scripts)
- The Groovy function output key is always "2"

```xml
<!-- Mapping: source booleanField (key=7) -> Groovy function 2 input -->
<Mapping fromKey="7" fromType="profile"
         toFunction="2" toKey="1" toType="function"/>

<!-- Mapping: Groovy function 2 output -> target resultField (key=8) -->
<Mapping fromFunction="2" fromKey="2" fromType="function"
         toKey="8" toType="profile"/>
```

```xml
<FunctionStep cacheEnabled="true" category="Scripting" key="2" name="MyConversion"
              position="2" sumEnabled="false" type="Scripting" x="10.0" y="150.0">
  <Inputs>
    <Input key="1" name="inputField"/>
  </Inputs>
  <Outputs>
    <Output key="2" name="outputField"/>
  </Outputs>
  <Configuration>
    <Scripting language="groovy2">
      <ScriptToExecute><![CDATA[
// Example: boolean true/false -> Y/N
if (inputField?.toString()?.trim()?.toLowerCase() == "true") {
    outputField = "Y"
} else {
    outputField = "N"
}
return [outputField]
      ]]></ScriptToExecute>
      <Input dataType="character" index="1" name="inputField"/>
      <Output index="2" name="outputField"/>
    </Scripting>
  </Configuration>
</FunctionStep>
```

**Position y values:** Space FunctionStep elements 140.0 apart. First at y=10.0, second at y=150.0, third at y=290.0, etc.
The `key` attribute must be unique within `<Functions>` and matches the `toFunction`/`fromFunction` values in mappings.

---

## Pattern 4: Default value (when source is empty or unmapped)

Applies a static fallback to a target field. Goes in `<Defaults>`, not in `<Mappings>`.
`toKey` is the target profile field key.

```xml
<Defaults>
  <Default toKey="4" value="9999"/>
</Defaults>
```

If there are no defaults, use an empty element: `<Defaults/>`

---

## Pattern 5: Concatenate two fields

Three mapping lines: two source fields -> concat function inputs, one concat output -> target.

```xml
<!-- Mapping: firstNameField -> concat input 1 -->
<Mapping fromKey="3" fromType="profile"
         toFunction="3" toKey="1" toType="function"/>

<!-- Mapping: lastNameField -> concat input 2 -->
<Mapping fromKey="4" fromType="profile"
         toFunction="3" toKey="2" toType="function"/>

<!-- Mapping: concat output -> target fullName -->
<Mapping fromFunction="3" fromKey="3" fromType="function"
         toKey="7" toType="profile"/>
```

```xml
<FunctionStep cacheEnabled="true" category="String" key="3" name="Concat Name"
              position="3" sumEnabled="false" type="Concat" x="10.0" y="290.0">
  <Inputs>
    <Input key="1" name="String 1"/>
    <Input key="2" name="String 2" default=" "/>
    <!-- key 2 default is the separator between the two values -->
  </Inputs>
  <Outputs>
    <Output key="3" name="Result"/>
  </Outputs>
  <Configuration/>
</FunctionStep>
```

**Note:** The concat output key is "3" (not "2"), and both input keys are "1" and "2".
You can chain more inputs by adding `<Input key="3" name="String 3"/>` etc.

---

## Key numbering rules

When writing `<Mapping>` elements, the `fromKey`/`toKey` values come directly from the profile XML:

| Profile type | Key offset for first data field |
|---|---|
| JSON | key=3 (after Root=1 and Object container=2) |
| XML | key=2 (after root element=1) |
| Flat File | key=2 (after Record=1) |
| Database | key=4 (after DBStatement=2 and DBFields=3) |

Always verify field keys in the profile XML before wiring mappings.
