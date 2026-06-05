# Boomi Profile XML Schemas

Use these validated templates when building profile components for map creation.
Pick the section that matches the profile type chosen by the user.

---

## JSON Profile (`type="profile.json"`)

Key offset: Root = key 1, Object container = key 2, Fields start at key 3.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bns:Component xmlns:bns="http://api.platform.boomi.com/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               name="MY_JSON_PROFILE"
               type="profile.json"
               folderId="FOLDER_ID">
  <bns:encryptedValues/>
  <bns:description>DESCRIPTION</bns:description>
  <bns:object>
    <JsonProfile xmlns="" strict="false">
      <ProfileProperties/>
      <DataElements>
        <ProfileElement isNode="true" key="1" name="Root" repeatable="false" type="Object">
          <ProfileElement isNode="true" key="2" name="Root" repeatable="false" type="Object">
            <ProfileElement isMappable="true" isNode="false" key="3" mandatory="false"
                           name="fieldOne" type="String"/>
            <ProfileElement isMappable="true" isNode="false" key="4" mandatory="false"
                           name="fieldTwo" type="String"/>
            <!-- Add more fields here, incrementing key by 1 each time -->
          </ProfileElement>
        </ProfileElement>
      </DataElements>
    </JsonProfile>
  </bns:object>
</bns:Component>
```

**JSON field `type` values:** `String`, `Number`, `Boolean`, `Date`, `Object`, `Array`

---

## XML Profile (`type="profile.xml"`)

Key offset: Root element = key 1, child elements start at key 2.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bns:Component xmlns:bns="http://api.platform.boomi.com/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               name="MY_XML_PROFILE"
               type="profile.xml"
               folderId="FOLDER_ID">
  <bns:encryptedValues/>
  <bns:description>DESCRIPTION</bns:description>
  <bns:object>
    <XMLProfile xmlns="" strict="false">
      <ProfileProperties>
        <XMLGeneralInfo rootElement="RootElementName" rootNamespace=""/>
      </ProfileProperties>
      <DataElements>
        <XMLElement isMappable="false" isNode="true" key="1" name="RootElementName"
                    namespace="" repeatable="false">
          <XMLElement isMappable="true" isNode="false" key="2" mandatory="false"
                      name="fieldOne" namespace="" repeatable="false" type="character"/>
          <XMLElement isMappable="true" isNode="false" key="3" mandatory="false"
                      name="fieldTwo" namespace="" repeatable="false" type="character"/>
          <!-- Add more fields here, incrementing key by 1 each time -->
        </XMLElement>
      </DataElements>
    </XMLProfile>
  </bns:object>
</bns:Component>
```

**XML field `type` values:** `character`, `number`, `integer`, `date`, `boolean`

---

## Flat File Profile (`type="profile.flatfile"`)

Key offset: Record = key 1, Fields start at key 2.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bns:Component xmlns:bns="http://api.platform.boomi.com/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               name="MY_FLAT_FILE_PROFILE"
               type="profile.flatfile"
               folderId="FOLDER_ID">
  <bns:encryptedValues/>
  <bns:description>DESCRIPTION</bns:description>
  <bns:object>
    <FlatFileProfile xmlns="" strict="false">
      <ProfileProperties>
        <FlatFileGeneralInfo recordSeparator="&#10;" fileCharacterSet="UTF-8"/>
      </ProfileProperties>
      <DataElements>
        <FlatFileRecord isNode="true" key="1" name="Record" repeatable="true"
                        fieldSeparator="," quotedFields="true"
                        recordIdentifierType="none" recordType="commadelimited">
          <FlatFileElement isMappable="true" isNode="false" key="2"
                           mandatory="false" name="fieldOne" type="character"/>
          <FlatFileElement isMappable="true" isNode="false" key="3"
                           mandatory="false" name="fieldTwo" type="character"/>
          <!-- Add more fields here, incrementing key by 1 each time -->
        </FlatFileRecord>
      </DataElements>
    </FlatFileProfile>
  </bns:object>
</bns:Component>
```

**Flat file field `type` values:** `character`, `number`, `integer`, `date`, `boolean`

**Note:** `recordType` must be `commadelimited` (all lowercase). For tab-delimited use `tabdelimited`.

---

## Database Profile (`type="profile.db"`)

Key offset: DBStatement = key 2, DBFields = key 3, Fields start at key 4.
The `xmlns=""` attribute on `<DatabaseProfile>` is required.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bns:Component xmlns:bns="http://api.platform.boomi.com/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               name="MY_DB_PROFILE"
               type="profile.db"
               folderId="FOLDER_ID">
  <bns:encryptedValues/>
  <bns:description>DESCRIPTION</bns:description>
  <bns:object>
    <DatabaseProfile xmlns="" strict="true" version="2">
      <ProfileProperties>
        <DatabaseGeneralInfo executionType="dbwrite"/>
      </ProfileProperties>
      <DataElements>
        <DBStatement isNode="true" key="2" name="Statement"
                     statementType="standardinsertupdatedelete"
                     storedProcedure="" tableName="">
          <DBFields isNode="true" key="3" name="Fields">
            <DatabaseElement enforceUnique="false" isMappable="true" isNode="true"
                             key="4" mandatory="false" name="fieldOne">
              <DataFormat><ProfileCharacterFormat/></DataFormat>
            </DatabaseElement>
            <DatabaseElement enforceUnique="false" isMappable="true" isNode="true"
                             key="5" mandatory="false" name="fieldTwo">
              <DataFormat><ProfileCharacterFormat/></DataFormat>
            </DatabaseElement>
            <!-- Add more fields here, incrementing key by 1 each time -->
          </DBFields>
          <sql></sql>
        </DBStatement>
      </DataElements>
    </DatabaseProfile>
  </bns:object>
</bns:Component>
```

**Database field data formats:**
- Character (text): `<DataFormat><ProfileCharacterFormat/></DataFormat>`
- Number: `<DataFormat><ProfileNumberFormat/></DataFormat>`
- Date: `<DataFormat><ProfileDateFormat dateFormat="yyyy-MM-dd"/></DataFormat>`

For a READ profile (SELECT), change `executionType="dbwrite"` to `executionType="dbread"` and `statementType` to `"standardselect"`.
