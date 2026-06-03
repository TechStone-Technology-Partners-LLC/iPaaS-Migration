# webMethods GLD — Complete Flow Logic & Migration Blueprint

> **Complete step-by-step logic extracted from all 202 active flow services across all packages.**
> Each INVOKE shows the exact service called. Each MAP shows field copies and constant assignments.
> BRANCH shows the switch field. LOOP shows the iterated variable. EXIT shows signal type.

---

## Package: GLDComplianceCheck

### `GLDComplianceCheck/MainFlows/complianceCheckRequest`

```
BRANCH on '/debug' [DISABLED]
  INVOKE '$default' [DISABLED]
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'True' [DISABLED]
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'getSMTPServer'
      service: WSRCommon.Utilities.FlowServices:getSMTPServer
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getProfileData'
      service: GLDComplianceCheck.Utilities.FlowServices:getProfileData
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'xmlStringToXMLNode'
      service: pub.xml:xmlStringToXMLNode
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'xmlNodeToDocument'
      service: pub.xml:xmlNodeToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'validateRequiredFields'
      service: GLDComplianceCheck.ProcessFlows:validateRequiredFields
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on '/ComplianceCheckRequestStatus/ComplianceCheckRequestStatus/Status'
      SEQUENCE 'PASS' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'validateFieldsFormat'
          service: GLDComplianceCheck.ProcessFlows:validateFieldsFormat
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/ComplianceCheckRequestStatus/ComplianceCheckRequestStatus/Status'
          SEQUENCE 'PASS' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
            INVOKE 'documentToXMLString'
              service: pub.xml:documentToXMLString
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            SEQUENCE '' exit-on=DONE
              INVOKE 'LogXMLResponse'
                service: GLDMessageLog:LogXMLResponse
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
            END-SEQUENCE
            INVOKE 'setResponse'
              service: pub.flow:setResponse
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
            INVOKE 'smtp'
              service: pub.client:smtp
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            MAP [mode=STANDALONE]
            END-MAP
            INVOKE 'logCheckRequest'
              service: GLDComplianceAdapterServices:logCheckRequest
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            MAP [mode=STANDALONE]
            END-MAP
            INVOKE 'publish'
              service: pub.publish:publish
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE 'FAIL' exit-on=FAILURE
            INVOKE 'documentToXMLString'
              service: pub.xml:documentToXMLString
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
            SEQUENCE '' exit-on=DONE
              INVOKE 'LogXMLResponse'
                service: GLDMessageLog:LogXMLResponse
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
            END-SEQUENCE
            INVOKE 'setResponse'
              service: pub.flow:setResponse
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
      SEQUENCE 'INCOMPLETE' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'documentToXMLString'
          service: pub.xml:documentToXMLString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
        SEQUENCE '' exit-on=DONE
          INVOKE 'LogXMLResponse'
            service: GLDMessageLog:LogXMLResponse
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
        INVOKE 'setResponse'
          service: pub.flow:setResponse
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    INVOKE 'publishStatsDoc'
      service: WSRProcessStatistics.MainFlows:publishStatsDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'setResponse'
      service: pub.flow:setResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'smtp'
      service: pub.client:smtp
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDComplianceCheck/MainFlows/performComplianceCheck`

```
BRANCH on '/debug' [DISABLED]
  INVOKE '$default' [DISABLED]
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'True' [DISABLED]
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'determineCheckRequestType'
      service: GLDComplianceCheck.ProcessFlows:determineCheckRequestType
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'mapRequestFieldsBasedOnCheckType'
      service: GLDComplianceCheck.ProcessFlows:mapRequestFieldsBasedOnCheckType
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'getSMTPServer'
      service: WSRCommon.Utilities.FlowServices:getSMTPServer
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getProfileData'
      service: GLDComplianceCheck.Utilities.FlowServices:getProfileData
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    RETRY max=1
      INVOKE 'http'
        service: pub.client:http
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/header/status'
  END-BRANCH
END-RETRY
INVOKE 'ByteArrayToString'
  service: WmTransformationServices:ByteArrayToString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=DONE
  INVOKE 'LogXMLResponse'
    service: GLDMessageLog:LogXMLResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'isPositiveNumber'
  service: GLDComplianceCheck.Utilities.FlowServices:isPositiveNumber
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/isPositive'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
LOOP over '?'
  INVOKE 'logCheckReply'
    service: GLDComplianceAdapterServices:logCheckReply
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-LOOP
INVOKE 'isNullOrBlank'
  service: GLDComplianceCheck.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
BRANCH on '/result'
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'false'
    service: GLDComplianceAdapterServices:logCheckReplyError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
INVOKE 'updateCIURefNbr'
  service: GLDComplianceAdapterServices:updateCIURefNbr
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'sendReply'
  service: GLDComplianceCheck.ProcessFlows:sendReply
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'publishStatsDoc'
  service: WSRProcessStatistics.MainFlows:publishStatsDoc
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'smtp'
    service: pub.client:smtp
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'publishErrorDoc'
    service: WSRProcessStatistics.MainFlows:publishErrorDoc
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDComplianceCheck/MainFlows/performComplianceCheck_OLD`

```
INVOKE 'savePipelineToFile' [DISABLED]
  service: pub.flow:savePipelineToFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'restorePipelineFromFile' [DISABLED]
  service: pub.flow:restorePipelineFromFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'determineCheckRequestType'
      service: GLDComplianceCheck.ProcessFlows:determineCheckRequestType
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'getSMTPServer'
      service: WSRCommon.Utilities.FlowServices:getSMTPServer
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getProfileData'
      service: GLDComplianceCheck.Utilities.FlowServices:getProfileData
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    RETRY max=1
      INVOKE 'http'
        service: pub.client:http
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/header/status'
  END-BRANCH
END-RETRY
INVOKE 'ByteArrayToString'
  service: WmTransformationServices:ByteArrayToString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=DONE
  INVOKE 'LogXMLResponse'
    service: GLDMessageLog:LogXMLResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'isPositiveNumber'
  service: GLDComplianceCheck.Utilities.FlowServices:isPositiveNumber
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/isPositive'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
LOOP over '?'
  INVOKE 'logCheckReply'
    service: GLDComplianceAdapterServices:logCheckReply
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-LOOP
INVOKE 'isNullOrBlank'
  service: GLDComplianceCheck.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
BRANCH on '/result'
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'false'
    service: GLDComplianceAdapterServices:logCheckReplyError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
INVOKE 'updateCIURefNbr'
  service: GLDComplianceAdapterServices:updateCIURefNbr
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'sendReply'
  service: GLDComplianceCheck.ProcessFlows:sendReply
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'publishStatsDoc'
  service: WSRProcessStatistics.MainFlows:publishStatsDoc
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'smtp'
    service: pub.client:smtp
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'publishErrorDoc'
    service: WSRProcessStatistics.MainFlows:publishErrorDoc
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDComplianceCheck/ProcessFlows/determineCheckRequestType`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on ''
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDComplianceCheck/ProcessFlows/determineCheckRequestType_OLD`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on ''
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDComplianceCheck/ProcessFlows/mapRequestFieldsBasedOnCheckType`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on ''
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDComplianceCheck/ProcessFlows/sendReply`

```
BRANCH on '/debug' [DISABLED]
  INVOKE '$default' [DISABLED]
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'True' [DISABLED]
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'getServiceName'
    service: WSRCommon.Utilities.JavaServices:getServiceName
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/ERROR'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'getSMTPServer'
    service: WSRCommon.Utilities.FlowServices:getSMTPServer
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'getProfileData'
    service: GLDComplianceCheck.Utilities.FlowServices:getProfileData
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  SEQUENCE '' exit-on=DONE
    RETRY max=%maxRetries%
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'http'
        service: pub.client:http
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
      END-MAP
      SEQUENCE '' exit-on=DONE
        INVOKE 'LogXMLRequest'
          service: GLDMessageLog:LogXMLRequest
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      BRANCH on '/header/status'
        SEQUENCE '200' exit-on=FAILURE
          INVOKE 'bytesToString'
            service: pub.string:bytesToString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          MAP [mode=STANDALONE]
          END-MAP
          SEQUENCE '' exit-on=DONE
            INVOKE 'LogXMLResponse'
              service: GLDMessageLog:LogXMLResponse
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'queryXMLNode'
            service: pub.xml:queryXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'publishStatsDoc'
            service: WSRProcessStatistics.MainFlows:publishStatsDoc
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlNodeToDocument'
            service: pub.xml:xmlNodeToDocument
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on '/ComplianceCheckReplyStatus/ComplianceCheckReplyStatus/Status'
            SEQUENCE 'PASS' exit-on=FAILURE
              MAP [mode=STANDALONE]
              END-MAP
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            BRANCH on ''
              SEQUENCE '%$retries% = %maxRetries%' exit-on=FAILURE
                MAP [mode=STANDALONE]
                END-MAP
                INVOKE 'smtp'
                  service: pub.client:smtp
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
            END-SEQUENCE
            SEQUENCE '$default' exit-on=FAILURE
              INVOKE 'concat'
                service: pub.string:concat
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      SEQUENCE '%$retries% = %maxRetries%' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'concat'
          service: pub.string:concat
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'smtp'
          service: pub.client:smtp
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      INVOKE 'concat'
        service: pub.string:concat
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
  END-SEQUENCE
END-BRANCH
END-SEQUENCE
END-BRANCH
END-RETRY
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'purgeData'
    service: GLDComplianceAdapterServices:purgeData
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDComplianceCheck/ProcessFlows/validateFieldsFormat`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'isNumericOrEmpty'
    service: GLDComplianceCheck.Utilities.FlowServices:isNumericOrEmpty
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/isNumeric'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '/SSNLength'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  INVOKE 'isNumericOrEmpty'
    service: GLDComplianceCheck.Utilities.FlowServices:isNumericOrEmpty
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/isNumeric'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  INVOKE 'isNumericOrEmpty'
    service: GLDComplianceCheck.Utilities.FlowServices:isNumericOrEmpty
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/isNumeric'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  INVOKE 'isNumericOrEmpty'
    service: GLDComplianceCheck.Utilities.FlowServices:isNumericOrEmpty
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/isNumeric'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  INVOKE 'isNumericOrEmpty'
    service: GLDComplianceCheck.Utilities.FlowServices:isNumericOrEmpty
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/isNumeric'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  INVOKE 'isNumericOrEmpty'
    service: GLDComplianceCheck.Utilities.FlowServices:isNumericOrEmpty
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/isNumeric'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  INVOKE 'addressValidation'
    service: GLDComplianceCheck.Utilities.FlowServices:addressValidation
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/isValid'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
BRANCH on '/ComplianceCheckRequestStatus/ComplianceCheckRequestStatus/Errors/Error[0]/ErrorCode'
  SEQUENCE '2' exit-on=FAILURE
    INVOKE 'documentListToDocument'
      service: pub.document:documentListToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'publishStatsDoc' [DISABLED]
  service: WSRProcessStatistics.MainFlows:publishStatsDoc
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDComplianceCheck/ProcessFlows/validateRequiredFields`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'isNullOrBlank'
      service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    BRANCH on ''
      SEQUENCE '%RequestData/ComplianceCheckRequest/Identification/PartyType%=&quot;Guarantor&quot; || %RequestData/ComplianceCheckRequest/Identification/CustomerType% = &quot;IND&quot;' exit-on=FAILURE
        INVOKE 'isNullOrBlank'
          service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/result'
          SEQUENCE 'true' exit-on=FAILURE
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
          END-SEQUENCE
          SEQUENCE 'false' exit-on=FAILURE
            LOOP over '?'
              BRANCH on ''
                MAP [mode=STANDALONE]
                  MAP [mode=INVOKEINPUT]
                  END-MAP
                  MAP [mode=INVOKEOUTPUT]
                  END-MAP
                END-MAP
            END-BRANCH
          END-LOOP
        END-SEQUENCE
      END-BRANCH
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'isNullOrBlank'
        service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/result'
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-BRANCH
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'isNullOrBlank'
        service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/result'
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-BRANCH
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'isNullOrBlank'
        service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/result'
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-BRANCH
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on ''
    SEQUENCE '%RequestData/ComplianceCheckRequest/Identification/PartyType%=&quot;Lessee&quot; || %RequestData/ComplianceCheckRequest/Identification/PartyType%=&quot;Guarantor&quot;' exit-on=FAILURE
      INVOKE 'isNullOrBlank'
        service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/result'
        SEQUENCE 'true' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
        SEQUENCE 'false' exit-on=FAILURE
          LOOP over '?'
            BRANCH on ''
              MAP [mode=STANDALONE]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
          END-BRANCH
        END-LOOP
      END-SEQUENCE
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/RequestData/ComplianceCheckRequest/Identification/CustomerType'
    SEQUENCE 'ORG' exit-on=FAILURE
      INVOKE 'isNullOrBlank'
        service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/result'
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-BRANCH
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/RequestData/ComplianceCheckRequest/AdditionalInformation/BatchOrOnline'
    SEQUENCE 'YES' exit-on=FAILURE
      INVOKE 'isNullOrBlank'
        service: GLDComplianceCheck.Utilities.JavaServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/result'
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-BRANCH
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
LOOP over '?'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-LOOP
END-SEQUENCE
INVOKE 'publishStatsDoc' [DISABLED]
  service: WSRProcessStatistics.MainFlows:publishStatsDoc
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDComplianceCheck/Utilities/FlowServices/addressValidation`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE] [DISABLED]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  LOOP over '?' [DISABLED]
    SEQUENCE '' exit-on=FAILURE [DISABLED]
      MAP [mode=STANDALONE] [DISABLED]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      BRANCH on '/addressLine1' [DISABLED]
        SEQUENCE '' exit-on=FAILURE [DISABLED]
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE [DISABLED]
        MAP [mode=STANDALONE] [DISABLED]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    MAP [mode=STANDALONE] [DISABLED]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on '' [DISABLED]
      SEQUENCE '%value% !=-1' exit-on=FAILURE [DISABLED]
        MAP [mode=STANDALONE] [DISABLED]
        END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE [DISABLED]
      MAP [mode=STANDALONE] [DISABLED]
      END-MAP
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE] [DISABLED]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '' [DISABLED]
    SEQUENCE '%value% !=-1' exit-on=FAILURE [DISABLED]
      MAP [mode=STANDALONE] [DISABLED]
      END-MAP
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% !=-1' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
END-SEQUENCE
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '' [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
  END-BRANCH
END-BRANCH
SEQUENCE '' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '' [DISABLED]
    SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
      MAP [mode=STANDALONE] [DISABLED]
      END-MAP
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE] [DISABLED]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '' [DISABLED]
  SEQUENCE '%value% &gt;= 0' exit-on=FAILURE [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
END-BRANCH
END-SEQUENCE
END-LOOP
BRANCH on '/addressLine1'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on ''
  SEQUENCE '%addressLength%&lt;=4' exit-on=FAILURE
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
```

### `GLDComplianceCheck/Utilities/FlowServices/getProfileData`

```
SEQUENCE '' exit-on=FAILURE
  INVOKE 'getInternalID'
    service: wm.tn.profile:getInternalID
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'getProfile'
    service: wm.tn.profile:getProfile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?'
    BRANCH on '/profile/Delivery/Protocol'
      BRANCH on ''
        SEQUENCE '%profile/Delivery/PrimaryAddr/MBoolean% =true' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
      END-BRANCH
      BRANCH on ''
        SEQUENCE '%profile/Delivery/PrimaryAddr/MBoolean% =true' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
        END-SEQUENCE
      END-BRANCH
      BRANCH on ''
        SEQUENCE '%profile/Delivery/PrimaryAddr/MBoolean% =true' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-BRANCH
  END-LOOP
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDComplianceCheck/Utilities/FlowServices/isNullOrBlank`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/outString'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDComplianceCheck/Utilities/FlowServices/isNumericOrEmpty`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    BRANCH on '/inNum'
      MAP [mode=STANDALONE]
      END-MAP
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        BRANCH on ''
          MAP [mode=STANDALONE]
          END-MAP
        END-BRANCH
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-SEQUENCE
```

### `GLDComplianceCheck/Utilities/FlowServices/isPositiveNumber`

```
MAP [mode=STANDALONE]
END-MAP
BRANCH on ''
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

## Package: GLDExpressGateway

### `GLDExpressGateway/MainFlows/CheckWriter/processCWRequest`

```
```

### `GLDExpressGateway/MainFlows/Customer/elCustomerUpdateTask`

```
INVOKE 'updateELCustomersFromLeasePk'
  service: GLDExpressGateway.MainFlows.Customer:updateELCustomersFromLeasePk
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/MainFlows/Customer/resetDataPointer`

```
BRANCH on '/newTime'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
INVOKE 'updateLPKCustomersProcessedDate'
  service: GLDExpressAdapterServices.Customer:updateLPKCustomersProcessedDate
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/MainFlows/Customer/runLpk2ELCustomerUpdate`

```
BRANCH on '/debugmsm7'
  INVOKE '$default'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
BRANCH on '/dbPullInstanceId'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on ''
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on '/startingDate'
  INVOKE '$default'
    service: GLDExpressAdapterServices.Customer:updateLPKCustomersProcessedDate
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'updateELCustomersFromLeasePk'
  service: GLDExpressGateway.MainFlows.Customer:updateELCustomersFromLeasePk
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
```

### `GLDExpressGateway/MainFlows/Customer/skipToEndOfData`

```
INVOKE 'initializeLPKCustomerUpdateData'
  service: GLDExpressAdapterServices.Customer:initializeLPKCustomerUpdateData
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'updateLPKCustomersProcessedDate'
  service: GLDExpressAdapterServices.Customer:updateLPKCustomersProcessedDate
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/MainFlows/Customer/updateELCustomersFromLeasePk`

```
BRANCH on '/chunkSize'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on '/dbPullInstanceId'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on '/initialLoad'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on '/maxChunkCount'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on '/startingChunk'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'initializeLPKCustomerUpdateData'
      service: GLDExpressAdapterServices.Customer:initializeLPKCustomerUpdateData
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    BRANCH on ''
      SEQUENCE '%initiateGetLpkCustomerChangesOutput/P_NEWPROCESSDATE% != $null || %initiateGetLpkCustomerChangesOutput/P_NEWPROCESSDATE% != ''' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        RETRY max=%dbChunkCount%
          INVOKE 'getRecentLPKCustomerChangesChunk'
            service: GLDExpressAdapterServices.Customer:getRecentLPKCustomerChangesChunk
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on ''
            SEQUENCE '%getRecentLPKCustomerChangesOutput/results% != $null' exit-on=FAILURE
              MAP [mode=STANDALONE]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
              BRANCH on ''
                SEQUENCE '%sizeOfCustomerLesseeDataList% &gt; 0' exit-on=FAILURE
                  MAP [mode=STANDALONE]
                    MAP [mode=INVOKEINPUT]
                    END-MAP
                    MAP [mode=INVOKEOUTPUT]
                    END-MAP
                  END-MAP
                  INVOKE 'groupLpkCustomerData'
                    service: GLDExpressGateway.ProcessFlows.Customer.JavaServices:groupLpkCustomerData
                    MAP [mode=INPUT]
                    END-MAP
                    MAP [mode=OUTPUT]
                    END-MAP
                  END-INVOKE
                  LOOP over '?'
                    MAP [mode=STANDALONE]
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                    END-MAP
                    INVOKE 'invokeProcessLpkCustomer'
                      service: GLDExpressGateway.ProcessFlows.Customer:invokeProcessLpkCustomer
                      MAP [mode=INPUT]
                      END-MAP
                      MAP [mode=OUTPUT]
                      END-MAP
                    END-INVOKE
                    MAP [mode=STANDALONE]
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                    END-MAP
                    BRANCH on ''
                      SEQUENCE '%errorcheck% != 'error'' exit-on=FAILURE
                        MAP [mode=STANDALONE]
                          MAP [mode=INVOKEINPUT]
                          END-MAP
                          MAP [mode=INVOKEOUTPUT]
                          END-MAP
                        END-MAP
                        MAP [mode=STANDALONE]
                          MAP [mode=INVOKEINPUT]
                          END-MAP
                          MAP [mode=INVOKEOUTPUT]
                          END-MAP
                        END-MAP
                        MAP [mode=STANDALONE]
                          MAP [mode=INVOKEINPUT]
                          END-MAP
                          MAP [mode=INVOKEOUTPUT]
                          END-MAP
                        END-MAP
                        MAP [mode=STANDALONE]
                          MAP [mode=INVOKEINPUT]
                          END-MAP
                          MAP [mode=INVOKEOUTPUT]
                          END-MAP
                          MAP [mode=INVOKEINPUT]
                          END-MAP
                          MAP [mode=INVOKEOUTPUT]
                          END-MAP
                        END-MAP
                        MAP [mode=STANDALONE]
                          MAP [mode=INVOKEINPUT]
                          END-MAP
                          MAP [mode=INVOKEOUTPUT]
                          END-MAP
                        END-MAP
                      END-SEQUENCE
                      SEQUENCE '$default' exit-on=FAILURE
                        SEQUENCE '' exit-on=DONE
                          MAP [mode=STANDALONE]
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                          END-MAP
                          MAP [mode=STANDALONE]
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                          END-MAP
                          MAP [mode=STANDALONE]
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                          END-MAP
                          MAP [mode=STANDALONE]
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                          END-MAP
                          MAP [mode=STANDALONE]
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                          END-MAP
                          MAP [mode=STANDALONE]
                            MAP [mode=INVOKEINPUT]
                            END-MAP
                            MAP [mode=INVOKEOUTPUT]
                            END-MAP
                          END-MAP
                          INVOKE 'LogXMLRequest'
                            service: GLDMessageLog:LogXMLRequest
                            MAP [mode=INPUT]
                            END-MAP
                            MAP [mode=OUTPUT]
                            END-MAP
                          END-INVOKE
                        END-SEQUENCE
                      END-SEQUENCE
                    END-BRANCH
                  END-LOOP
                  MAP [mode=STANDALONE]
                  END-MAP
                  SEQUENCE '' exit-on=DONE
                    MAP [mode=STANDALONE]
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                    END-MAP
                    MAP [mode=STANDALONE]
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                    END-MAP
                    MAP [mode=STANDALONE]
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                    END-MAP
                    INVOKE 'LogXMLRequest'
                      service: GLDMessageLog:LogXMLRequest
                      MAP [mode=INPUT]
                      END-MAP
                      MAP [mode=OUTPUT]
                      END-MAP
                    END-INVOKE
                  END-SEQUENCE
                END-SEQUENCE
                SEQUENCE '$default' exit-on=FAILURE
                  MAP [mode=STANDALONE]
                  END-MAP
                END-SEQUENCE
              END-BRANCH
            END-SEQUENCE
            SEQUENCE '$default' exit-on=FAILURE
          END-SEQUENCE
        END-BRANCH
        BRANCH on ''
      END-BRANCH
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-RETRY
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on ''
      SEQUENCE '%errorcheck% != 'error'' exit-on=FAILURE
        INVOKE 'updateLPKCustomersProcessedDate'
          service: GLDExpressAdapterServices.Customer:updateLPKCustomersProcessedDate
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        SEQUENCE '' exit-on=DONE
          INVOKE 'LogXMLRequest'
            service: GLDMessageLog:LogXMLRequest
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
END-SEQUENCE
END-BRANCH
INVOKE 'currentDate'
  service: pub.date:currentDate
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'publishErrorDoc'
  service: WSRProcessStatistics.MainFlows:publishErrorDoc
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=DONE
  INVOKE 'LogXMLRequest'
    service: GLDMessageLog:LogXMLRequest
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  SEQUENCE '' exit-on=DONE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  INVOKE 'publishErrorDoc'
    service: WSRProcessStatistics.MainFlows:publishErrorDoc
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/MainFlows/EFW/processLXIRequest`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getTransportInfo'
      service: pub.flow:getTransportInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'xmlNodeToDocument'
      service: pub.xml:xmlNodeToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'getEfwServiceNameToInvoke'
        service: GLDExpressGateway.Utilities.FlowServices:getEfwServiceNameToInvoke
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeServiceThrowExceptions'
        service: GLDExpressGateway.Utilities.JavaServices:invokeServiceThrowExceptions
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeServiceThrowExceptions' [DISABLED]
        service: WSRCommon.Utilities.JavaServices:invokeServiceThrowExceptions
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'getDebugInfo'
        service: WSRProcessStatistics.ProcessFlows:getDebugInfo
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/DebugInfo/EFW'
        SEQUENCE '/.+/' exit-on=FAILURE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'publishStatsDoc'
            service: WSRProcessStatistics.MainFlows:publishStatsDoc
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'createErrorResponse'
      service: GLDExpressGateway.ProcessFlows.EFW:createErrorResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/MainFlows/EFW/processLXIRequest_1_unknown`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getTransportInfo'
      service: pub.flow:getTransportInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'xmlNodeToDocument'
      service: pub.xml:xmlNodeToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'getEfwServiceNameToInvoke_1'
        service: GLDExpressGateway.Utilities.FlowServices:getEfwServiceNameToInvoke_1
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'getEfwServiceNameToInvoke_1' [DISABLED]
        service: GLDExpressGateway.Utilities.FlowServices:getEfwServiceNameToInvoke_1
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeService_1'
        service: WSRCommon.Utilities.JavaServices:invokeService_1
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'getDebugInfo'
        service: WSRProcessStatistics.ProcessFlows:getDebugInfo
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/DebugInfo/EFW'
        SEQUENCE '/.+/' exit-on=FAILURE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'publishStatsDoc'
            service: WSRProcessStatistics.MainFlows:publishStatsDoc
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/MainFlows/EFW/processLXIRequest_9_25_08_bu`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getTransportInfo'
      service: pub.flow:getTransportInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'xmlNodeToDocument'
      service: pub.xml:xmlNodeToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'getEfwServiceNameToInvoke'
        service: GLDExpressGateway.Utilities.FlowServices:getEfwServiceNameToInvoke
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeService_1'
        service: WSRCommon.Utilities.JavaServices:invokeService_1
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'getDebugInfo'
        service: WSRProcessStatistics.ProcessFlows:getDebugInfo
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/DebugInfo/EFW'
        SEQUENCE '/.+/' exit-on=FAILURE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'publishStatsDoc'
            service: WSRProcessStatistics.MainFlows:publishStatsDoc
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'setResponse'
      service: pub.flow:setResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/MainFlows/EFW/processLXIRequest_9_9_08_bu`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getTransportInfo'
      service: pub.flow:getTransportInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'isUserAssignedGLDgroups'
      service: GLDExpressGateway.Utilities.FlowServices:isUserAssignedGLDgroups
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'xmlNodeToDocument'
      service: pub.xml:xmlNodeToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: GLDExpressGateway.Utilities.FlowServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'serviceExists'
      service: GLDExpressGateway.Utilities.JavaServices:serviceExists
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/Result' [DISABLED]
      INVOKE 'True' [DISABLED]
        service: WSRCommon.Utilities.JavaServices:invokeService_1
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE '$default' [DISABLED]
        service: GLDExpressGateway.ProcessFlows.EFW:invokeDefaultRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '' [DISABLED]
        INVOKE 'throwsServerException' [DISABLED]
          service: WSRCommon.Utilities.JavaServices:throwsServerException
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-BRANCH
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      SEQUENCE 'service == &quot;RefDataRequest&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        BRANCH on ''
          SEQUENCE 'indexGLD &gt;= 0' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-BRANCH
    BRANCH on ''
      SEQUENCE '(isGldUser ==&quot;true&quot; &amp;&amp; Result == &quot;True&quot;) || (isGLDRefData == &quot;true&quot;)' exit-on=FAILURE
        INVOKE 'invokeService_1'
          service: WSRCommon.Utilities.JavaServices:invokeService_1
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        INVOKE 'invokeDefaultRequest'
          service: GLDExpressGateway.ProcessFlows.EFW:invokeDefaultRequest
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      BRANCH on ''
        INVOKE 'throwsServerException'
          service: WSRCommon.Utilities.JavaServices:throwsServerException
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-BRANCH
    END-BRANCH
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'getDebugInfo'
      service: WSRProcessStatistics.ProcessFlows:getDebugInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/DebugInfo/EFW'
      SEQUENCE '/.+/' exit-on=FAILURE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        INVOKE 'publishStatsDoc'
          service: WSRProcessStatistics.MainFlows:publishStatsDoc
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/MainFlows/EFW/processLXIRequest_Ryan_9_9`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getTransportInfo'
      service: pub.flow:getTransportInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'xmlNodeToDocument'
      service: pub.xml:xmlNodeToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'getEfwServiceNameToInvoke'
        service: GLDExpressGateway.Utilities.FlowServices:getEfwServiceNameToInvoke
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeService_1'
        service: WSRCommon.Utilities.JavaServices:invokeService_1
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'getDebugInfo'
        service: WSRProcessStatistics.ProcessFlows:getDebugInfo
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/DebugInfo/EFW'
        SEQUENCE '/.+/' exit-on=FAILURE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'publishStatsDoc'
            service: WSRProcessStatistics.MainFlows:publishStatsDoc
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-SEQUENCE
  MAP [mode=STANDALONE]
  END-MAP
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/MainFlows/EFW/processLXIRequest_ryan_bu`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getTransportInfo'
      service: pub.flow:getTransportInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'xmlNodeToDocument'
      service: pub.xml:xmlNodeToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'getEfwServiceNameToInvoke'
        service: GLDExpressGateway.Utilities.FlowServices:getEfwServiceNameToInvoke
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeService_1'
        service: WSRCommon.Utilities.JavaServices:invokeService_1
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'getDebugInfo'
        service: WSRProcessStatistics.ProcessFlows:getDebugInfo
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/DebugInfo/EFW'
        SEQUENCE '/.+/' exit-on=FAILURE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'publishStatsDoc'
            service: WSRProcessStatistics.MainFlows:publishStatsDoc
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-SEQUENCE
  MAP [mode=STANDALONE]
  END-MAP
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/MainFlows/VMSMT/processVMRequest`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'queryXMLNode'
      service: pub.xml:queryXMLNode
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'xmlNodeToDocument'
      service: pub.xml:xmlNodeToDocument
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on ''
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'invokeXML_HTTP'
      service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/status'
      SEQUENCE '200' exit-on=FAILURE
        INVOKE 'xmlStringToXMLNode'
          service: pub.xml:xmlStringToXMLNode
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'queryXMLNode'
          service: pub.xml:queryXMLNode
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        INVOKE 'setResponse'
          service: pub.flow:setResponse
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on ''
          SEQUENCE '%service%!=&quot;ErrorResponse&quot;' exit-on=FAILURE
            INVOKE 'serviceExists'
              service: GLDExpressGateway.Utilities.JavaServices:serviceExists
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            BRANCH on '/Result'
              SEQUENCE 'True' exit-on=FAILURE
                INVOKE 'invokeServiceThrowExceptions'
                  service: GLDExpressGateway.Utilities.JavaServices:invokeServiceThrowExceptions
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
                INVOKE 'invokeServiceThrowExceptions' [DISABLED]
                  service: WSRCommon.Utilities.JavaServices:invokeServiceThrowExceptions
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
              END-SEQUENCE
            END-BRANCH
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        INVOKE 'setResponse'
          service: pub.flow:setResponse
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
    INVOKE 'publishStatsDoc'
      service: WSRProcessStatistics.MainFlows:publishStatsDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'setResponse'
      service: pub.flow:setResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'LogXMLResponse'
      service: GLDMessageLog:LogXMLResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/AddExternalSystemID`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    RETRY max=3
      INVOKE 'invokeXML_HTTP'
        service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-RETRY
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
END-SEQUENCE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/App/invokeAppDetailsRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/requestType'
  SEQUENCE 'GetAppRequest' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'invokeGetAppDetailsFromXLink'
      service: GLDExpressGateway.ProcessFlows.App:invokeGetAppDetailsFromXLink
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE 'AppHomeRequest' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'invokeGetAppDetailsFromXLink'
      service: GLDExpressGateway.ProcessFlows.App:invokeGetAppDetailsFromXLink
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/App/invokeGetAppDetailsFromXLink`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
SEQUENCE '' exit-on=FAILURE
  LOOP over '?'
    BRANCH on '/GetTransactionDetailsSoapOut/tns1:GetTransactionDetailsResponse/tns1:GetTransactionDetailsResult/tns1:assignedUsers/tns1:assignedUser/tns1:appUserTypeId'
      SEQUENCE '103' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '104' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-LOOP
END-SEQUENCE
BRANCH on ''
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeGetCreditDecision'
  service: GLDExpressGateway.ProcessFlows:invokeGetCreditDecision
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  LOOP over '?'
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
      BRANCH on '/Canonical_GetTransactionApplicantsSoapOut/tns1:GetTransactionApplicantsResponse/tns1:GetTransactionApplicantsResult/tns1:applicant/tns1:companyDetails/tns1:addresses/tns1:address/tns1:addressCategories/tns1:addressCategory/tns1:addressCategoryIds'
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
    END-LOOP
  END-LOOP
  LOOP over '?'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
    LOOP over '?'
      LOOP over '?'
        BRANCH on '/Canonical_GetTransactionApplicantsSoapOut/tns1:GetTransactionApplicantsResponse/tns1:GetTransactionApplicantsResult/tns1:transactionConsumerRelatedParties/tns1:transactionConsumerRelatedParty/tns1:consumer/tns1:addresses/tns1:address/tns1:addressCategories/tns1:addressCategory/tns1:addressCategoryIds'
          MAP [mode=STANDALONE]
          END-MAP
          SEQUENCE '$default' exit-on=FAILURE
          END-SEQUENCE
        END-BRANCH
      END-LOOP
    END-LOOP
  END-LOOP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?'
    MAP [mode=STANDALONE]
    END-MAP
    LOOP over '?'
      INVOKE 'invokeGetVendorDetailsByGldId'
        service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      BRANCH on '/AssetCondition'
        SEQUENCE 'U' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
        SEQUENCE 'N' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-LOOP
  END-LOOP
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/Applicant/getXLinkApplicantId`

```
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'invokeDandBMatch'
      service: GLDExpressGateway.ProcessFlows.Applicant:invokeDandBMatch
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on ''
      SEQUENCE 'dnbResultCount=1' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        LOOP over '?'
          INVOKE 'appendToStringList'
            service: pub.list:appendToStringList
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-LOOP
      END-SEQUENCE
      SEQUENCE 'dnbResultCount&gt;=1' exit-on=FAILURE
        LOOP over '?'
          INVOKE 'appendToStringList'
            service: pub.list:appendToStringList
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-LOOP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'invokeXLinkMatch'
      service: GLDExpressGateway.ProcessFlows.Applicant:invokeXLinkMatch
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
BRANCH on '/gldApplicantCount'
  SEQUENCE '0' exit-on=FAILURE
    INVOKE 'invokeSaveEFWApplicant'
      service: GLDExpressGateway.ProcessFlows.Applicant:invokeSaveEFWApplicant
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    INVOKE 'invokeApplicantMatch'
      service: GLDExpressGateway.ProcessFlows.Applicant:invokeApplicantMatch
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/Applicant/invokeApplicantMatch`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  LOOP over '?'
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        LOOP over '?'
          MAP [mode=STANDALONE]
          END-MAP
          BRANCH on '/Canonical_KEFCustomerSearchSoapOut/tns1:KEFCustomerSearchResponse/tns1:KEFCustomerSearchResult/tns1:customerCompaniesSearchResults/tns1:customerCompanySearchResults/tns1:customerCompanyAddressesResponse/tns1:customerCompanyAddressesResponse/tns1:customerSearchAddressCategories/tns1:customerSearchAddressCategory/tns1:addressCategoryId'
            MAP [mode=STANDALONE]
            END-MAP
            SEQUENCE '3' exit-on=FAILURE
              MAP [mode=STANDALONE]
              END-MAP
              MAP [mode=STANDALONE]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
            END-SEQUENCE
          END-BRANCH
        END-LOOP
      END-LOOP
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        BRANCH on '/Canonical_KEFCustomerSearchSoapOut/tns1:KEFCustomerSearchResponse/tns1:KEFCustomerSearchResult/tns1:customerCompaniesSearchResults/tns1:customerCompanySearchResults/tns1:customerCompanyContactsResponse/tns1:customerCompanyContactResponse/tns1:ContactType'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-BRANCH
      END-LOOP
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        MAP [mode=STANDALONE]
        END-MAP
        BRANCH on ''
          SEQUENCE '%CompanyId%=%SignorCompanyId%' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
            SEQUENCE '' exit-on=FAILURE
              LOOP over '?'
                LOOP over '?'
                  BRANCH on '/Canonical_KEFCustomerSearchSoapOut/tns1:KEFCustomerSearchResponse/tns1:KEFCustomerSearchResult/tns1:customerSignorsSearchResults/tns1:customerSignorSearchResults/tns1:customerSignorAddressesResponse/tns1:customerSignorAddressResponse/tns1:customerSearchAddressCategories/tns1:customerSearchAddressCategory/tns1:addressCategoryId'
                    MAP [mode=STANDALONE]
                    END-MAP
                  END-BRANCH
                END-LOOP
              END-LOOP
            END-SEQUENCE
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
          END-SEQUENCE
        END-BRANCH
      END-LOOP
    END-SEQUENCE
    INVOKE 'invokeXOS_EFWApplicantMatch'
      service: GLDExpressGateway.ProcessFlows.Applicant.JavaServices:invokeXOS_EFWApplicantMatch
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/MatchCode'
      SEQUENCE 'Exact' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
    END-SEQUENCE
    SEQUENCE 'Similar' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
    END-SEQUENCE
  END-BRANCH
END-LOOP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on ''
    SEQUENCE 'result=true || XLinkApplicantId=0' exit-on=FAILURE
      SEQUENCE '' exit-on=SUCCESS
        SEQUENCE '' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          BRANCH on ''
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
          END-BRANCH
          INVOKE 'invokeSaveEFWApplicant'
            service: GLDExpressGateway.ProcessFlows.Applicant:invokeSaveEFWApplicant
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
        SEQUENCE '' exit-on=DONE
          INVOKE 'getLastError'
            service: pub.flow:getLastError
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'LogXMLRequest'
            service: GLDMessageLog:LogXMLRequest
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
      END-SEQUENCE
    END-SEQUENCE
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/Applicant/invokeDandBMatch`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'buildSecHdr'
  service: WSRCommon.WebServices:buildSecHdr
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/Applicant/invokeGetTransactionApplicants`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/Applicant/invokeSaveEFWApplicant`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'invokeXOSGenericSaveApplicant'
    service: GLDExpressGateway.ProcessFlows.Applicant:invokeXOSGenericSaveApplicant
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXLinkCustomFieldSave'
    service: GLDExpressGateway.ProcessFlows:invokeXLinkCustomFieldSave
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/Applicant/invokeSaveEFWPrincipal`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/Contact/State'
  SEQUENCE '$null' exit-on=FAILURE
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'invokeXOSGenericSaveApplicant'
  service: GLDExpressGateway.ProcessFlows.Applicant:invokeXOSGenericSaveApplicant
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/Applicant/invokeXLinkMatch`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/Applicant/invokeXOSGenericSaveApplicant`

```
BRANCH on '/Canonical_XOSGenericSaveApplicantSoapIn/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:riskRatingEvaluation'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
INVOKE 'prepareSaveApplicantMessage'
  service: GLDExpressGateway.ProcessFlows.Customer:prepareSaveApplicantMessage
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/AppID'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/Applicant/invokeXOSGetApplicant`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/CheckWriter/invokeAddNewPayee`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeCheckWriter'
    service: GLDExpressGateway.Utilities.FlowServices:invokeCheckWriter
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on ''
    SEQUENCE '%response% = /Unable to save changes/' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
  END-SEQUENCE
  SEQUENCE '%response% = /&quot;PAYEE_KEY&quot; value=&quot;/' exit-on=FAILURE
    INVOKE 'indexOf'
      service: pub.string:indexOf
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'addInts'
      service: pub.math:addInts
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'indexOf'
      service: pub.string:indexOf
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'substring'
      service: pub.string:substring
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/CheckWriter/invokeCreateCheckRequest`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeCheckWriter'
    service: GLDExpressGateway.Utilities.FlowServices:invokeCheckWriter
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on ''
    SEQUENCE '%response% = /Unable to save changes/' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
  END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/CheckWriter/invokeGetUniquePayee`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeCheckWriter'
    service: GLDExpressGateway.Utilities.FlowServices:invokeCheckWriter
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on ''
    SEQUENCE '%response% = /&quot;RSB_RECORD_COUNT&quot; value=&quot;1&quot;/' exit-on=FAILURE
      INVOKE 'indexOf'
        service: pub.string:indexOf
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'addInts'
        service: pub.math:addInts
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'indexOf'
        service: pub.string:indexOf
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'substring'
        service: pub.string:substring
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
END-SEQUENCE
END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/Compliance/invokeComplianceCheckBatch`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    BRANCH on ''
      SEQUENCE 'EntityID&gt;0' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        INVOKE 'invokeXML_SOAP'
          service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/Customer/JavaServices/checkJavaCodeVersion`

```
INVOKE 'versionCheck'
  service: GLDExpressGateway.ProcessFlows.Customer.JavaServices:versionCheck
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/Customer/assignCustomFieldIds`

```
LOOP over '?'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  LOOP over '?'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    INVOKE 'lookupCustomFieldIdBasedOnName'
      service: GLDExpressGateway.Utilities.FlowServices:lookupCustomFieldIdBasedOnName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-LOOP
  MAP [mode=STANDALONE]
  END-MAP
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/Customer/createSaveApplicantFromLpk2XosData`

```
BRANCH on '/msmdb3' [DISABLED]
  INVOKE '$default' [DISABLED]
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true' [DISABLED]
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  SEQUENCE '' exit-on=FAILURE
    LOOP over '?'
      SEQUENCE '' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        INVOKE 'lookupCountryFromProvince' [DISABLED]
          service: GLDExpressGateway.Utilities.FlowServices:lookupCountryFromProvince
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        LOOP over '?'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
          END-MAP
        END-LOOP
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-LOOP
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    LOOP over '?'
      SEQUENCE '' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        LOOP over '?'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
          END-MAP
        END-LOOP
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-LOOP
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getELBusinessType'
      service: GLDExpressGateway.Utilities.FlowServices:getELBusinessType
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'lookupSICIDBySIC'
      service: GLDExpressGateway.ProcessFlows.Customer.JavaServicesTemp:lookupSICIDBySIC
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'lookupNAICSIDByNAICS'
      service: GLDExpressGateway.ProcessFlows.Customer.JavaServicesTemp2:lookupNAICSIDByNAICS
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/xosParentCompanyId'
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/Customer/invokeCustomerLesseeDataUpdateProcess`

```
BRANCH on '/msmdebug' [DISABLED]
  INVOKE '$default' [DISABLED]
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true' [DISABLED]
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=FAILURE
  SEQUENCE '$default' exit-on=FAILURE
    LOOP over '?'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-LOOP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'invokeXML_SOAP' [DISABLED]
            service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
      END-SEQUENCE
    END-BRANCH
    BRANCH on '/customerNumber'
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'invokeXML_SOAP' [DISABLED]
            service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
  END-SEQUENCE
  BRANCH on '/Canonical_GetApplicantSoapOut/tns1:GetApplicantResponse/tns1:GetApplicantResult/tns1:applicant'
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'getELBusinessType'
        service: GLDExpressGateway.Utilities.FlowServices:getELBusinessType
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'lookupSICBySICID'
        service: GLDExpressGateway.ProcessFlows.Customer.JavaServicesTemp:lookupSICBySICID
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'lookupNAICSByNAICSID'
        service: GLDExpressGateway.ProcessFlows.Customer.JavaServicesTemp2:lookupNAICSByNAICSID
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      LOOP over '?'
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        LOOP over '?'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
          END-MAP
        END-LOOP
      END-LOOP
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  SEQUENCE '' exit-on=SUCCESS
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'determineXLinkCustomerUpdate'
        service: GLDExpressGateway.ProcessFlows.Customer.JavaServices:determineXLinkCustomerUpdate
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=DONE
      INVOKE 'getLastError'
        service: pub.flow:getLastError
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
  END-SEQUENCE
  BRANCH on '/result'
    SEQUENCE 'ok' exit-on=FAILURE
      INVOKE 'createSaveApplicantFromLpk2XosData'
        service: GLDExpressGateway.ProcessFlows.Customer:createSaveApplicantFromLpk2XosData
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'prepareSaveApplicantMessage' [DISABLED]
        service: GLDExpressGateway.ProcessFlows.Customer:prepareSaveApplicantMessage
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'assignCustomFieldIds' [DISABLED]
        service: GLDExpressGateway.ProcessFlows.Customer:assignCustomFieldIds
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'invokeSaveUpdatedCustomer'
          service: GLDExpressGateway.ProcessFlows.Customer:invokeSaveUpdatedCustomer
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/Customer/invokeProcessLpkCustomer`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'invokeCustomerLesseeDataUpdateProcess'
      service: GLDExpressGateway.ProcessFlows.Customer:invokeCustomerLesseeDataUpdateProcess
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/Customer/invokeSaveUpdatedCustomer`

```
BRANCH on '/msmdebug4' [DISABLED]
  INVOKE '$default' [DISABLED]
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true' [DISABLED]
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'invokeXOSGenericSaveApplicant'
      service: GLDExpressGateway.ProcessFlows.Applicant:invokeXOSGenericSaveApplicant
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/Canonical_XOSGenericSaveApplicantSoapOut/tns1:XOSGenericSaveApplicantResponse/tns1:XOSGenericSaveApplicantResult/tns1:errors'
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'documentToXMLString'
          service: pub.xml:documentToXMLString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        INVOKE 'documentToXMLString'
          service: pub.xml:documentToXMLString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
      SEQUENCE '$null' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
        END-MAP
        BRANCH on '/applicantId'
          MAP [mode=STANDALONE]
          END-MAP
        END-BRANCH
        BRANCH on '/applicantId'
          SEQUENCE '0' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
            INVOKE 'documentToXMLString'
              service: pub.xml:documentToXMLString
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            INVOKE 'documentToXMLString'
              service: pub.xml:documentToXMLString
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            INVOKE 'documentToXMLString' [DISABLED]
              service: pub.xml:documentToXMLString
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'invokeXML_SOAP' [DISABLED]
              service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            BRANCH on '/initialLoad'
              SEQUENCE 'true' exit-on=FAILURE
              END-SEQUENCE
              SEQUENCE '$default' exit-on=FAILURE
                INVOKE 'invokeComplianceCheckBatch'
                  service: GLDExpressGateway.ProcessFlows.Compliance:invokeComplianceCheckBatch
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
              END-SEQUENCE
            END-BRANCH
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/Customer/prepareSaveApplicantMessage`

```
BRANCH on '/msmdb2' [DISABLED]
  INVOKE '$default' [DISABLED]
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true' [DISABLED]
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails'
  SEQUENCE '$default' exit-on=FAILURE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:bankDetails/tns1:bankDetail/tns1:dateAccountOpened'
          MAP [mode=STANDALONE]
          END-MAP
        END-BRANCH
      END-LOOP
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:addresses/tns1:address/tns1:country'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-BRANCH
        BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:addresses/tns1:address/tns1:statusId'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-BRANCH
      END-LOOP
      BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:bankDetails'
        MAP [mode=STANDALONE]
        END-MAP
        SEQUENCE '$default' exit-on=FAILURE
          BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:bankDetails/tns1:bankDetail'
            MAP [mode=STANDALONE]
            END-MAP
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
          END-BRANCH
          BRANCH on '/bdcount'
            MAP [mode=STANDALONE]
            END-MAP
          END-BRANCH
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
      END-BRANCH
      BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:addresses'
        MAP [mode=STANDALONE]
        END-MAP
        SEQUENCE '$default' exit-on=FAILURE [DISABLED]
          BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:addresses/tns1:address' [DISABLED]
            MAP [mode=STANDALONE] [DISABLED]
            END-MAP
            MAP [mode=STANDALONE] [DISABLED]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
          END-BRANCH
          BRANCH on '/addrList' [DISABLED]
            MAP [mode=STANDALONE] [DISABLED]
            END-MAP
          END-BRANCH
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
        END-SEQUENCE
      END-BRANCH
      SEQUENCE '' exit-on=FAILURE
        BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:billingCompanies'
          MAP [mode=STANDALONE]
          END-MAP
          SEQUENCE '$default' exit-on=FAILURE
            LOOP over '?'
              SEQUENCE '' exit-on=FAILURE
                MAP [mode=STANDALONE]
                END-MAP
                MAP [mode=STANDALONE]
                END-MAP
              END-SEQUENCE
            END-LOOP
            BRANCH on '/billingCompany'
              SEQUENCE '$default' exit-on=FAILURE
                MAP [mode=STANDALONE]
                END-MAP
                MAP [mode=STANDALONE]
                END-MAP
              END-SEQUENCE
              MAP [mode=STANDALONE]
              END-MAP
            END-BRANCH
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE [DISABLED]
            BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:billingCompanies/tns1:billingCompany' [DISABLED]
              MAP [mode=STANDALONE] [DISABLED]
              END-MAP
              MAP [mode=STANDALONE] [DISABLED]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
            END-BRANCH
            BRANCH on '/bclist' [DISABLED]
              MAP [mode=STANDALONE] [DISABLED]
              END-MAP
            END-BRANCH
            MAP [mode=STANDALONE] [DISABLED]
            END-MAP
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
      BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:otherBusinessNames'
        MAP [mode=STANDALONE]
        END-MAP
        SEQUENCE '$default' exit-on=FAILURE [DISABLED]
          BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:companyDetails/tns1:otherBusinessNames/tns1:otherBusinessName' [DISABLED]
            MAP [mode=STANDALONE] [DISABLED]
            END-MAP
            MAP [mode=STANDALONE] [DISABLED]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
          END-BRANCH
          BRANCH on '/bdcount' [DISABLED]
            MAP [mode=STANDALONE] [DISABLED]
            END-MAP
          END-BRANCH
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '$null' exit-on=FAILURE
  END-SEQUENCE
END-BRANCH
BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:consumerDetails'
  SEQUENCE '$default' exit-on=FAILURE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:consumerDetails/tns1:addresses/tns1:address/tns1:country'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-BRANCH
        BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:consumerDetails/tns1:addresses/tns1:address/tns1:entityStatusId'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-BRANCH
      END-LOOP
      BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:consumerDetails/tns1:bankDetails'
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
      BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:consumerDetails/tns1:addresses'
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
      BRANCH on '/saveApplicant/tns1:XOSGenericSaveApplicant/tns1:applicantSaveDetail/tns1:consumerDetails/tns1:otherBusinessNames'
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '$null' exit-on=FAILURE
  END-SEQUENCE
END-BRANCH
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=FAILURE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/EFW/buildTransactionAssetSaveInput`

```
MAP [mode=STANDALONE]
END-MAP
LOOP over '?'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on ''
    SEQUENCE '%assetCondition%=0' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '%assetCondition%=1' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
  END-BRANCH
  INVOKE 'getWmForXLinkUserId'
    service: GLDExpressGateway.Utilities.FlowServices:getWmForXLinkUserId
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/AppSubmitRequest/SBSRequest/AppSubmitRequest/ScheduleList/Schedule/UseBusinessAddress'
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE '$default'
      service: GLDExpressGateway.ProcessFlows.EFW:getXLinkAddressId
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on '/vendorIdNotProvided'
      MAP [mode=STANDALONE]
      END-MAP
      SEQUENCE '$default' exit-on=FAILURE
        INVOKE 'invokeGetVendorDetailsByGldId'
          service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/GldSupplierId'
          SEQUENCE '0' exit-on=FAILURE
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            INVOKE 'invokeUpdateVendorInXLink'
              service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorInXLink
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'invokeGetVendorDetailsByGldId'
              service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'appendToDocumentList'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  MAP [mode=STANDALONE]
  END-MAP
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/concatenateAppSubmitVendorContacts`

```
MAP [mode=STANDALONE]
END-MAP
LOOP over '?'
  INVOKE 'invokeGetVendorContacts'
    service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorContacts
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?'
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
      BRANCH on ''
        SEQUENCE 'VMR_ID=EFW_ID' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-LOOP
  END-LOOP
  MAP [mode=STANDALONE]
  END-MAP
END-LOOP
LOOP over '?' [DISABLED]
  INVOKE 'invokeGetVendorContacts' [DISABLED]
    service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorContacts
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?' [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE] [DISABLED]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE] [DISABLED]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE] [DISABLED]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-LOOP
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-LOOP
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'length'
    service: pub.string:length
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/stringLength'
    SEQUENCE '0' exit-on=FAILURE
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/EFW/concatenateAppSubmitVendorContacts_1`

```
MAP [mode=STANDALONE]
END-MAP
LOOP over '?' [DISABLED]
  INVOKE 'invokeGetVendorContacts' [DISABLED]
    service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorContacts
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?' [DISABLED]
    LOOP over '?' [DISABLED]
      BRANCH on '' [DISABLED]
        SEQUENCE 'AppSubmitRequest/SBSRequest/AppSubmitRequest/VendorList/Vendor/RepresentativeList/Representative/RepresentativeId = VendorContactResponse/Envelope/Service/Vendor/ContactList/Contact/ContactId' exit-on=FAILURE [DISABLED]
          MAP [mode=STANDALONE] [DISABLED]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE] [DISABLED]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE] [DISABLED]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE] [DISABLED]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-LOOP
  END-LOOP
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-LOOP
LOOP over '?'
  INVOKE 'invokeGetVendorContacts'
    service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorContacts
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-LOOP
  MAP [mode=STANDALONE]
  END-MAP
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/createErrorResponse`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    BRANCH on '/ErrorResponse/SBSResponse/ErrorResponse/DebugInfo/LastMessageLogID'
      SEQUENCE '$null' exit-on=FAILURE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-BRANCH
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'setResponse'
      service: pub.flow:setResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'setResponse'
      service: pub.flow:setResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/EFW/getXLinkAddressId`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
LOOP over '?'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on ''
    SEQUENCE '%Address%=%XLinkAddress%' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
  END-SEQUENCE
END-BRANCH
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/getXLinkBusinessNameId`

```
LOOP over '?'
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on ''
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeAddApplicantAddresses`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'invokeXOSGetApplicant'
    service: GLDExpressGateway.ProcessFlows.Applicant:invokeXOSGetApplicant
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    SEQUENCE 'true' exit-on=FAILURE
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      LOOP over '?'
        BRANCH on ''
          SEQUENCE '%AppSubmitRequest/SBSRequest/AppSubmitRequest/Customer/DBAName%=%Canonical_GetApplicantSoapOut/tns1:GetApplicantResponse/tns1:GetApplicantResult/tns1:applicant/tns1:companyDetails/tns1:otherBusinessNames/tns1:otherBusinessName/tns1:otherBusinessName%' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
        END-SEQUENCE
      END-BRANCH
    END-LOOP
    BRANCH on '/foundDBA'
      SEQUENCE 'false' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  LOOP over '?'
    BRANCH on '/AppSubmitRequest/SBSRequest/AppSubmitRequest/ScheduleList/Schedule/UseBusinessAddress'
      MAP [mode=STANDALONE]
      END-MAP
      SEQUENCE '$default' exit-on=FAILURE
        INVOKE 'invokeInsertAddress'
          service: GLDExpressGateway.ProcessFlows.EFW:invokeInsertAddress
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-LOOP
  INVOKE 'invokeInsertAddress'
    service: GLDExpressGateway.ProcessFlows.EFW:invokeInsertAddress
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/updateRequired'
    SEQUENCE 'true' exit-on=FAILURE
      INVOKE 'prepareSaveApplicantMessage'
        service: GLDExpressGateway.ProcessFlows.Customer:prepareSaveApplicantMessage
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeXOSGenericSaveApplicant'
        service: GLDExpressGateway.ProcessFlows.Applicant:invokeXOSGenericSaveApplicant
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeAddCommentRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'getCurrentDateString'
  service: pub.date:getCurrentDateString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'lookUpCommentTypeDescription'
  service: GLDExpressGateway.ProcessFlows.Supplemental:lookUpCommentTypeDescription
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXosGenericXmlTransactionNotesSave'
  service: GLDExpressGateway.ProcessFlows:invokeXosGenericXmlTransactionNotesSave
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeAppHomeRequest`

```
INVOKE 'invokeAppDetailsRequest'
  service: GLDExpressGateway.ProcessFlows.App:invokeAppDetailsRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeAppSearchRequest`

```
INVOKE 'savePipelineToFile' [DISABLED]
  service: pub.flow:savePipelineToFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'restorePipelineFromFile' [DISABLED]
  service: pub.flow:restorePipelineFromFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
SEQUENCE 'Query LXI' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_HTTP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'getDocument'
    service: GLDExpressGateway.Utilities.FlowServices:getDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?'
    INVOKE 'isNullOrBlank'
      service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/LxiAppSearchResponse/SBSResponse/AppSearchResponse/ApplicationList/Application/InitialAppEntryTime'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-LOOP
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE 'Query ExpressLink' exit-on=FAILURE
  INVOKE 'xmlStringToXMLNode'
    service: pub.xml:xmlStringToXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlNodeToDocument'
    service: pub.xml:xmlNodeToDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    SEQUENCE '' exit-on=FAILURE
      SEQUENCE '' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-SEQUENCE
    SEQUENCE 'Set Search Criteria' exit-on=FAILURE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'isNullOrBlank'
          service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/notSourceSpecificSearch'
          SEQUENCE 'true' exit-on=FAILURE
          END-SEQUENCE
          SEQUENCE 'false' exit-on=FAILURE
            INVOKE 'invokeGetVendorDetailsByGldId'
              service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
        BRANCH on '/AppSearchRequest/SBSRequest/AppSearchRequest/User/UnrestrictedSwitch'
          SEQUENCE '1' exit-on=FAILURE
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            INVOKE 'invokeUserPermissionInfoRequest'
              service: GLDExpressGateway.ProcessFlows.EFW:invokeUserPermissionInfoRequest
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'invokeGetRgrpGldIdsRequest'
              service: GLDExpressGateway.ProcessFlows.VMR:invokeGetRgrpGldIdsRequest
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            BRANCH on '/notSourceSpecificSearch'
              SEQUENCE 'true' exit-on=FAILURE
                LOOP over '?'
                  BRANCH on '/$iteration'
                    MAP [mode=STANDALONE]
                    END-MAP
                    MAP [mode=STANDALONE]
                      MAP [mode=INVOKEINPUT]
                      END-MAP
                      MAP [mode=INVOKEOUTPUT]
                      END-MAP
                    END-MAP
                  END-BRANCH
                  MAP [mode=STANDALONE]
                    MAP [mode=INVOKEINPUT]
                    END-MAP
                    MAP [mode=INVOKEOUTPUT]
                    END-MAP
                  END-MAP
                END-LOOP
              END-SEQUENCE
              SEQUENCE 'false' exit-on=FAILURE
                LOOP over '?'
                  BRANCH on ''
                    MAP [mode=STANDALONE]
                    END-MAP
                    MAP [mode=STANDALONE]
                    END-MAP
                  END-BRANCH
                END-LOOP
                INVOKE 'isNullOrBlank'
                  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
                BRANCH on '/userDoesNotHavePermission'
                  MAP [mode=STANDALONE]
                  END-MAP
              END-BRANCH
            END-SEQUENCE
          END-BRANCH
        END-SEQUENCE
      END-BRANCH
      INVOKE 'isNullOrBlank'
        service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/originatorListNotProvided'
        INVOKE 'false'
          service: pub.list:appendToDocumentList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-BRANCH
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'isNullOrBlank'
        service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/result'
        INVOKE 'false'
          service: pub.list:appendToDocumentList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'isNullOrBlank'
      service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/result'
      INVOKE 'false'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
  END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE 'false' exit-on=FAILURE
      INVOKE 'invokeGetVendorDetailsByGldId'
        service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-BRANCH
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    INVOKE 'false'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-BRANCH
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    INVOKE 'false'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-BRANCH
END-SEQUENCE
SEQUENCE 'Set Status Date Start' exit-on=FAILURE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-BRANCH
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
END-SEQUENCE
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/AppSearchResponseXOS/tns1:XosGenericApplicationSearchResponse/tns1:XosGenericApplicationSearchResult/tns1:totalResultCount'
    SEQUENCE '1' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
    LOOP over '?'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-LOOP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on ''
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'sortDocumentList'
    service: GLDExpressGateway.Utilities.JavaServices:sortDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?'
    BRANCH on ''
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-LOOP
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeAppSearchRequest_9_12_08_bu`

```
SEQUENCE '' exit-on=FAILURE [DISABLED]
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
  INVOKE 'invokeXML_HTTP' [DISABLED]
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'xmlStringToXMLNode'
    service: pub.xml:xmlStringToXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlNodeToDocument'
    service: pub.xml:xmlNodeToDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    INVOKE 'false'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-BRANCH
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    INVOKE 'false'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-BRANCH
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    INVOKE 'false'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-BRANCH
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    INVOKE 'false'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-BRANCH
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-BRANCH
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE 'false' exit-on=FAILURE
      INVOKE 'invokeGetVendorDetailsByGldId'
        service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  INVOKE 'isNullOrBlank'
    service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/result'
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE 'false' exit-on=FAILURE
      INVOKE 'invokeGetVendorDetailsByGldId'
        service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  LOOP over '?'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE] [DISABLED]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE] [DISABLED]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-LOOP
  INVOKE 'sortDocumentList' [DISABLED]
    service: GLDExpressGateway.Utilities.JavaServices:sortDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeAppSubmitRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeSaveEFWApplicant' [DISABLED]
  service: GLDExpressGateway.ProcessFlows.Applicant:invokeSaveEFWApplicant
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getXLinkApplicantId'
  service: GLDExpressGateway.ProcessFlows.Applicant:getXLinkApplicantId
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeAddApplicantAddresses'
    service: GLDExpressGateway.ProcessFlows.EFW:invokeAddApplicantAddresses
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'invokeXOSGetApplicant'
    service: GLDExpressGateway.ProcessFlows.Applicant:invokeXOSGetApplicant
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'getXLinkAddressId'
    service: GLDExpressGateway.ProcessFlows.EFW:getXLinkAddressId
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'getXLinkBusinessNameId'
    service: GLDExpressGateway.ProcessFlows.EFW:getXLinkBusinessNameId
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'buildTransactionAssetSaveInput'
  service: GLDExpressGateway.ProcessFlows.EFW:buildTransactionAssetSaveInput
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'getCurrentDateString'
  service: pub.date:getCurrentDateString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXosGenericXmlTransactionSave'
  service: GLDExpressGateway.ProcessFlows:invokeXosGenericXmlTransactionSave
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'concatenateAppSubmitVendorContacts'
  service: GLDExpressGateway.ProcessFlows.EFW:concatenateAppSubmitVendorContacts
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXLinkCustomFieldSave'
  service: GLDExpressGateway.ProcessFlows:invokeXLinkCustomFieldSave
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXosGenericXmlTransactionAssetsSave'
  service: GLDExpressGateway.ProcessFlows:invokeXosGenericXmlTransactionAssetsSave
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
BRANCH on '/result'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'invokeXosGenericXmlTransactionNotesSave'
      service: GLDExpressGateway.ProcessFlows:invokeXosGenericXmlTransactionNotesSave
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeRelatedPartyRequest'
  service: GLDExpressGateway.ProcessFlows:invokeRelatedPartyRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
BRANCH on '/SubmitToCredit'
  SEQUENCE 'true' exit-on=FAILURE
    INVOKE 'publishSubmitToCredit'
      service: GLDExpressGateway.ProcessFlows:publishSubmitToCredit
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeChargeListRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionAssets'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionAssets
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
    END-LOOP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    LOOP over '?'
      LOOP over '?'
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'compareDates'
            service: GLDExpressGateway.Utilities.JavaServices:compareDates
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'compareDates'
            service: GLDExpressGateway.Utilities.JavaServices:compareDates
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
        SEQUENCE '' exit-on=FAILURE
          BRANCH on ''
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
          END-BRANCH
        END-SEQUENCE
      END-LOOP
    END-LOOP
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    LOOP over '?'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-LOOP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    SEQUENCE '' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      LOOP over '?'
        LOOP over '?'
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-LOOP
      END-LOOP
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'invokeGetTransactionApplicants'
        service: GLDExpressGateway.ProcessFlows.Applicant:invokeGetTransactionApplicants
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'setResponse'
      service: pub.flow:setResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeCommentListRequest`

```
BRANCH on '/debug'
  INVOKE '$null'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=FAILURE
  INVOKE 'xmlStringToXMLNode'
    service: pub.xml:xmlStringToXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlNodeToDocument'
    service: pub.xml:xmlNodeToDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/CommentListRequest/SBSRequest/CommentListRequest/User/Type'
    SEQUENCE '1' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      LOOP over '?'
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        BRANCH on '/isInternalUser'
          SEQUENCE 'true' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE 'false' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
            INVOKE 'appendToDocumentList'
              service: pub.list:appendToDocumentList
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-LOOP
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  LOOP over '?'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-LOOP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionDetails'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionDetails
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeCommentTypeListRequest`

```
SEQUENCE '' exit-on=FAILURE
  INVOKE 'xmlStringToXMLNode'
    service: pub.xml:xmlStringToXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlNodeToDocument'
    service: pub.xml:xmlNodeToDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'getFixedCommentTypeList'
    service: GLDExpressGateway.ProcessFlows.Supplemental:getFixedCommentTypeList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'setResponse'
    service: pub.flow:setResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeDefaultRequest`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeDocumentListRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionDetails'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionDetails
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionApplicants'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionApplicants
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeEquipmentStructureRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionDetails'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionDetails
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionApplicants'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionApplicants
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeGetAppRequest`

```
INVOKE 'invokeAppDetailsRequest'
  service: GLDExpressGateway.ProcessFlows.App:invokeAppDetailsRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeGetDecisionRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetCreditDecision'
    service: GLDExpressGateway.ProcessFlows:invokeGetCreditDecision
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  LOOP over '?'
    MAP [mode=STANDALONE]
    END-MAP
  END-LOOP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionDetails'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionDetails
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  LOOP over '?'
    BRANCH on '/Canonical_GetTransactionDetailsSoapOut/tns1:GetTransactionDetailsResponse/tns1:GetTransactionDetailsResult/tns1:assignedUsers/tns1:assignedUser/tns1:appUserTypeId'
      SEQUENCE '6' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-LOOP
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionApplicants'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionApplicants
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeGetLeaseStructureRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionDetails'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionDetails
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionApplicants'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionApplicants
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeImageListRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionDetails'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionDetails
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetTransactionApplicants'
    service: GLDExpressGateway.ProcessFlows:invokeGetTransactionApplicants
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeInsertAddress`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
LOOP over '?'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on ''
    SEQUENCE '%Address%=%XLinkAddress%' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      LOOP over '?'
        LOOP over '?'
          BRANCH on ''
            SEQUENCE '%/addressCategory/tns1:category%=%applicantAddresses/tns1:addressCategories/tns1:addressCategory/tns1:category%' exit-on=FAILURE
              MAP [mode=STANDALONE]
              END-MAP
          END-SEQUENCE
        END-BRANCH
      END-LOOP
      BRANCH on '/categoryFound'
        SEQUENCE 'true' exit-on=FAILURE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-LOOP
END-SEQUENCE
END-BRANCH
END-LOOP
BRANCH on '/addressFound'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    INVOKE 'appendToDocumentList'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeLoginRequest`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'processScreenButtonPerms'
  service: GLDExpressGateway.ProcessFlows:processScreenButtonPerms
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeNewAppDataRequest`

```
BRANCH on '/debug'
  INVOKE '$default'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=FAILURE
  INVOKE 'xmlStringToXMLNode'
    service: pub.xml:xmlStringToXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlNodeToDocument'
    service: pub.xml:xmlNodeToDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_HTTP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlStringToXMLNode'
    service: pub.xml:xmlStringToXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlNodeToDocument'
    service: pub.xml:xmlNodeToDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on '/UserType'
      SEQUENCE '1' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'invokeXML_SOAP'
          service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '2' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'documentToXMLString'
          service: pub.xml:documentToXMLString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'xmlStringToXMLNode'
          service: pub.xml:xmlStringToXMLNode
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'processVMRequest'
          service: GLDExpressGateway.MainFlows.VMSMT:processVMRequest
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'xmlStringToXMLNode'
          service: pub.xml:xmlStringToXMLNode
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'xmlNodeToDocument'
          service: pub.xml:xmlNodeToDocument
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'setResponse'
    service: pub.flow:setResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeRefDataRequest`

```
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeXML_HTTP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlStringToXMLNode'
    service: pub.xml:xmlStringToXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlNodeToDocument'
    service: pub.xml:xmlNodeToDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'insertLegalBusinessTypes'
    service: GLDExpressGateway.ProcessFlows:insertLegalBusinessTypes
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'insertAssetInformation'
    service: GLDExpressGateway.ProcessFlows:insertAssetInformation
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  SEQUENCE '' exit-on=FAILURE
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
    END-LOOP
  END-SEQUENCE
  SEQUENCE '' exit-on=FAILURE
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
    END-LOOP
  END-SEQUENCE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'setResponse'
    service: pub.flow:setResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeStatusHistoryRequest`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  LOOP over '?'
    BRANCH on ''
      SEQUENCE '%Canonical_GetTransactionStatusHistorySoapOut/tns1:GetTransactionStatusHistoryResponse/tns1:GetTransactionStatusHistoryResult/tns1:transStatusHistoryResponse/tns1:transStatusesHistoryResponse/tns1:statusId% == 0' exit-on=FAILURE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        BRANCH on ''
          SEQUENCE '%startDesc% == %newDesc%' exit-on=FAILURE
            INVOKE 'getDateDiff'
              service: GLDExpressGateway.Utilities.FlowServices:getDateDiff
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            BRANCH on ''
              MAP [mode=STANDALONE]
              END-MAP
              SEQUENCE '$default' exit-on=FAILURE
                MAP [mode=STANDALONE]
                  MAP [mode=INVOKEINPUT]
                  END-MAP
                  MAP [mode=INVOKEOUTPUT]
                  END-MAP
                END-MAP
                MAP [mode=STANDALONE]
                END-MAP
              END-SEQUENCE
            END-BRANCH
          END-SEQUENCE
          MAP [mode=STANDALONE]
          END-MAP
        END-BRANCH
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-LOOP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'setResponse'
  service: pub.flow:setResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeUserPermissionInfoRequest`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/UserPermissionInfoRequest/Envelope/Service/Response'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
SEQUENCE '' exit-on=FAILURE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/EFW/invokeUserSourcePermissionCheckRequest`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/Supplemental/getFixedCommentTypeList`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/Supplemental/lookUpCommentTypeDescription`

```
INVOKE 'getFixedCommentTypeList'
  service: GLDExpressGateway.ProcessFlows.Supplemental:getFixedCommentTypeList
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
LOOP over '?'
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on ''
    SEQUENCE 'currentCode = code' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
  END-SEQUENCE
END-BRANCH
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeChangeStatusRequest`

```
INVOKE 'savePipelineToFile' [DISABLED]
  service: pub.flow:savePipelineToFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'restorePipelineFromFile' [DISABLED]
  service: pub.flow:restorePipelineFromFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
BRANCH on ''
  SEQUENCE '(%code%=15 or %code%=19)' exit-on=FAILURE
    BRANCH on ''
      INVOKE '%GldOriginatorId%!=null &amp; %GldSupplierId%!=null'
        service: GLDExpressGateway.ProcessFlows:invokeXOSDataLoader
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    INVOKE 'invokeXOSDataLoader'
      service: GLDExpressGateway.ProcessFlows:invokeXOSDataLoader
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeDeleteVendorContactRequest`

```
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeUpdateVendorInXLink'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorInXLink
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeGetContact`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeGetExcludeInterimRent`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeGetVendorConstructs'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorConstructs
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
LOOP over '?'
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on ''
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeGetIsProrataAppliedValue`

```
INVOKE 'invokeGetExcludeInterimRent'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeGetExcludeInterimRent
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on ''
  SEQUENCE 'result='true'' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE 'result='false'' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeGetRgrpGldIdsRequest`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeGetVendorConstructs`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeGetVendorContacts`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeGetVendorDetailsByGldId`

```
INVOKE 'getVMSMTUserConstants'
  service: GLDExpressGateway.Utilities.FlowServices:getVMSMTUserConstants
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeMapVmrContactsToGld`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '/noDisableContactId'
    SEQUENCE 'false' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'invokeGetContact'
        service: GLDExpressGateway.ProcessFlows.VMR:invokeGetContact
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      INVOKE 'appendToDocumentList'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
LOOP over '?'
  BRANCH on '/gldEntityType'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on ''
    SEQUENCE '%noAchAccountNumberExists% = &quot;false&quot; &amp;&amp; %noAchRoutingNumberExists% = &quot;false&quot;' exit-on=FAILURE
      BRANCH on '/noGldAccountNumberExists'
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '%noAchAccountNumberExists% = &quot;true&quot; &amp;&amp; %noAchRoutingNumberExists% = &quot;true&quot;' exit-on=FAILURE
      BRANCH on ''
        SEQUENCE '%noGldAccountNumberExists% = &quot;false&quot;' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-BRANCH
  BRANCH on ''
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-BRANCH
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeUpdateContactGldIDsRequest`

```
MAP [mode=STANDALONE]
END-MAP
LOOP over '?'
  BRANCH on ''
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
END-LOOP
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXML_HTTP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeUpdateVendorApprovals`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/CorpOnlyApproval/Code'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/CorpOnlyDecline/Code'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/PGApproval/Code'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/PGDecline/Code'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/CorpOnlyApproval/Code'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/CorpOnlyDecline/Code'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/PGApproval/Code'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/PGDecline/Code'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeUpdateVendorConstructsRequest`

```
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeUpdateVendorInXLink'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorInXLink
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeUpdateVendorContactRequest`

```
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeUpdateVendorInXLink'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorInXLink
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeUpdateVendorCreditDataRequest`

```
BRANCH on '/debug'
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE '$default'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
INVOKE 'LogXMLRequest'
  service: GLDMessageLog:LogXMLRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeUpdateVendorInXLink'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorInXLink
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeUpdateVendorInXLink`

```
INVOKE 'invokeGetVendorDetailsByGldId'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE] [DISABLED]
END-MAP
INVOKE 'documentToXMLString' [DISABLED]
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeXML_HTTP' [DISABLED]
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getDocument' [DISABLED]
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on ''
  SEQUENCE '%gldSupplierIdNotNull% = &quot;false&quot; || %vendorStatusCode% = 15 || %vendorStatusCode% = 16 || %vendorStatusCode% = 17' exit-on=FAILURE
    INVOKE 'invokeXOSDataLoader'
      service: GLDExpressGateway.ProcessFlows:invokeXOSDataLoader
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeUpdateVendorRequest`

```
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeUpdateVendorInXLink'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorInXLink
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/VMR/invokeUpdateVendorServicingRequest`

```
INVOKE 'getDocument'
  service: GLDExpressGateway.Utilities.FlowServices:getDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeUpdateVendorInXLink'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorInXLink
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/getCustomerLesseeData`

```
```

### `GLDExpressGateway/ProcessFlows/insertAssetInformation`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'sortDocumentList'
    service: GLDExpressGateway.Utilities.JavaServices:sortDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  LOOP over '?'
    BRANCH on '/RefDataAssetCategories/AssetCategory/Code'
      SEQUENCE '0' exit-on=FAILURE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        INVOKE 'invokeXML_SOAP'
          service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        LOOP over '?'
          MAP [mode=STANDALONE]
          END-MAP
        END-LOOP
        INVOKE 'appendToDocumentList'
          service: pub.list:appendToDocumentList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
  END-LOOP
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/insertLegalBusinessTypes`

```
SEQUENCE '' exit-on=FAILURE
  INVOKE 'getTNProfile'
    service: GLDExpressGateway.Utilities.FlowServices:getTNProfile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/invokeGetCreditDecision`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/invokeGetTransactionApplicants`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/invokeGetTransactionAssets`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/invokeGetTransactionDetails`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/invokeRelatedPartyRequest`

```
LOOP over '?'
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on ''
    SEQUENCE '%EFW_RelatedPartyType%=1' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '%EFW_RelatedPartyType%=2' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '%EFW_RelatedPartyType%=3' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
  END-BRANCH
  INVOKE 'invokeXosGenericRelatedPartySave'
    service: GLDExpressGateway.ProcessFlows:invokeXosGenericRelatedPartySave
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/invokeSubmitToCredit`

```
BRANCH on '/debug'
  INVOKE '$null'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'getTNProfile'
      service: GLDExpressGateway.Utilities.FlowServices:getTNProfile
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    RETRY max=3
      INVOKE 'invokeXML_SOAP'
        service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-RETRY
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSMTPServer'
      service: WSRCommon.Utilities.FlowServices:getSMTPServer
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'smtp'
      service: pub.client:smtp
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/invokeTransactionAssetCustomFieldSave`

```
INVOKE 'savePipelineToFile' [DISABLED]
  service: pub.flow:savePipelineToFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'restorePipelineFromFile' [DISABLED]
  service: pub.flow:restorePipelineFromFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeGetTransactionAssets'
  service: GLDExpressGateway.ProcessFlows:invokeGetTransactionAssets
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=FAILURE [DISABLED]
  LOOP over '?' [DISABLED]
    MAP [mode=STANDALONE] [DISABLED]
    END-MAP
    INVOKE 'appendToDocumentList' [DISABLED]
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-LOOP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  LOOP over '?'
    INVOKE 'invokeFindMatchInList'
      service: GLDExpressGateway.Utilities.FlowServices:invokeFindMatchInList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-LOOP
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/invokeTransactionContactInformationSave`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeXLinkCustomFieldSave'
  service: GLDExpressGateway.ProcessFlows:invokeXLinkCustomFieldSave
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/invokeXLinkCustomFieldSave`

```
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/invokeXOSDataLoader`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/GldOriginatorId'
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/GldSupplierId'
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'invokeXOSDataLoaderSuppliers'
      service: GLDExpressGateway.ProcessFlows:invokeXOSDataLoaderSuppliers
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'AddExternalSystemID'
      service: GLDExpressGateway.ProcessFlows:AddExternalSystemID
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/Type'
      SEQUENCE '2' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'invokeXOSDataLoaderOriginators'
          service: GLDExpressGateway.ProcessFlows:invokeXOSDataLoaderOriginators
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'documentToXMLString'
          service: pub.xml:documentToXMLString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'AddExternalSystemID'
          service: GLDExpressGateway.ProcessFlows:AddExternalSystemID
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
      END-SEQUENCE
    END-BRANCH
    INVOKE 'publishStatsDoc'
      service: WSRProcessStatistics.MainFlows:publishStatsDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/invokeXOSDataLoaderOriginators`

```
BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/GldOriginatorId'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/Address/GLDOriginatorAddressId'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeGetVendorContacts'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorContacts
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeMapVmrContactsToGld'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeMapVmrContactsToGld
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeGetIsProrataAppliedValue'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeGetIsProrataAppliedValue
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeMatchVMR_ID_to_XLink_ID'
  service: GLDExpressGateway.Utilities.FlowServices:invokeMatchVMR_ID_to_XLink_ID
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on ''
  SEQUENCE '%noAchAccountNumberExists% = &quot;false&quot; &amp;&amp; %noAchRoutingNumberExists% = &quot;false&quot;' exit-on=FAILURE
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE '%noAchAccountNumberExists% = &quot;true&quot; &amp;&amp; %noAchRoutingNumberExists% = &quot;true&quot;' exit-on=FAILURE
    BRANCH on ''
      SEQUENCE '%noGldOriginatorBankAccountIIdExists% = &quot;false&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
END-BRANCH
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on ''
  SEQUENCE '%result%=true||%OriginatorId%=0' exit-on=FAILURE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '%result%=false||%OriginatorId%&gt;0' exit-on=FAILURE
    INVOKE 'invokeComplianceCheckBatch'
      service: GLDExpressGateway.ProcessFlows.Compliance:invokeComplianceCheckBatch
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
LOOP over '?'
  INVOKE 'invokeUpdateContactGldIDsRequest'
    service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateContactGldIDsRequest
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'invokeUpdateVendorApprovals'
    service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorApprovals
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-LOOP
INVOKE 'publishStatsDoc'
  service: WSRProcessStatistics.MainFlows:publishStatsDoc
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/invokeXOSDataLoaderSuppliers`

```
BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/GldSupplierId'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/Address/GLDSupplierAddressId'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'invokeGetVendorContacts'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorContacts
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeMapVmrContactsToGld'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeMapVmrContactsToGld
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'invokeMatchVMR_ID_to_XLink_ID'
  service: GLDExpressGateway.Utilities.FlowServices:invokeMatchVMR_ID_to_XLink_ID
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on ''
  SEQUENCE '%noAchAccountNumberExists% = &quot;false&quot; &amp;&amp; %noAchRoutingNumberExists% = &quot;false&quot;' exit-on=FAILURE
    BRANCH on ''
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
    END-BRANCH
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE '%noAchAccountNumberExists% = &quot;true&quot; &amp;&amp; %noAchRoutingNumberExists% = &quot;true&quot;' exit-on=FAILURE
    BRANCH on ''
      SEQUENCE '%noGldSupplierBankAccountIdExists% = &quot;false&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
END-BRANCH
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on ''
  SEQUENCE '%result%=true||%Canonical_XosGenericXmlSuppliersSaveResponse/tns1:XosGenericXmlSuppliersSaveResponse/tns1:XosGenericXmlSuppliersSaveResult/tns1:SupplierResponses/tns1:SupplierResponse[0]/tns1:SupplierID%=0' exit-on=FAILURE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '%result%=false||%Canonical_XosGenericXmlSuppliersSaveResponse/tns1:XosGenericXmlSuppliersSaveResponse/tns1:XosGenericXmlSuppliersSaveResult/tns1:SupplierResponses/tns1:SupplierResponse[0]/tns1:SupplierID%&gt;0' exit-on=FAILURE
    INVOKE 'invokeComplianceCheckBatch'
      service: GLDExpressGateway.ProcessFlows.Compliance:invokeComplianceCheckBatch
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
INVOKE 'invokeUpdateContactGldIDsRequest'
  service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateContactGldIDsRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'publishStatsDoc'
  service: WSRProcessStatistics.MainFlows:publishStatsDoc
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/invokeXosGenericRelatedPartySave`

```
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeSaveEFWPrincipal'
    service: GLDExpressGateway.ProcessFlows.Applicant:invokeSaveEFWPrincipal
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '/relatedPartyTypeID'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-BRANCH
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXLinkCustomFieldSave'
    service: GLDExpressGateway.ProcessFlows:invokeXLinkCustomFieldSave
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/invokeXosGenericXmlTransactionAssetsSave`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  LOOP over '?'
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
      LOOP over '?'
        BRANCH on ''
          SEQUENCE '%TransactionAssetsCustomFields/Assets/Asset/IntegrationCode%=%Canonical_XosGenericXmlTransactionAssetsSaveSoapOut/tns1:XosGenericXmlTransactionAssetsSaveResponse/tns1:XosGenericXmlTransactionAssetsSaveResult/tns1:transAssetResponses/tns1:transAssetResponse/tns1:transAssetDetailResponse/tns1:transAssetDetail/tns1:integrationCode%' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
            INVOKE 'appendToDocumentList'
              service: pub.list:appendToDocumentList
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-LOOP
  END-LOOP
END-LOOP
INVOKE 'invokeXLinkCustomFieldSave'
  service: GLDExpressGateway.ProcessFlows:invokeXLinkCustomFieldSave
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/invokeXosGenericXmlTransactionAssetsSave_8_16_08`

```
LOOP over '?'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on ''
    SEQUENCE '%assetCondition%=0' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '%assetCondition%=1' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
  END-BRANCH
  INVOKE 'getWmForXLinkUserId'
    service: GLDExpressGateway.Utilities.FlowServices:getWmForXLinkUserId
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeGetVendorDetailsByGldId'
    service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/invokeXosGenericXmlTransactionNotesSave`

```
MAP [mode=STANDALONE]
END-MAP
LOOP over '?'
  INVOKE 'getWmForXLinkUserId'
    service: GLDExpressGateway.Utilities.FlowServices:getWmForXLinkUserId
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'invokeXML_SOAP'
    service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/invokeXosGenericXmlTransactionSave`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  LOOP over '?'
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
      LOOP over '?'
        MAP [mode=STANDALONE]
        END-MAP
        BRANCH on '/Can_XosGenericXmlTransaction/tns1:XosGenericXmlTransactionSave/tns1:transaction/tns1:transactionLocationAddresses/tns1:transactionLocationAddress/tns1:transAddressId'
          SEQUENCE '%Canonical_XosGenericXmlTransactionAssets/tns1:XosGenericXmlTransactionAssetsSave/tns1:transAssetCollection/tns1:transAssets/tns1:transAsset/tns1:transAssetDetails/tns1:transAssetDetail/tns1:locationAddressId%' exit-on=FAILURE
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-BRANCH
      END-LOOP
      BRANCH on '/LocationAlreadyExists'
        SEQUENCE 'true' exit-on=FAILURE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-LOOP
  END-LOOP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'invokeGetVendorDetailsByGldId'
    service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/VendorId'
    SEQUENCE '0' exit-on=FAILURE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
  END-SEQUENCE
  BRANCH on '/VendorDataResponse/Envelope/Service/Vendor/GldOriginatorId'
    SEQUENCE '0' exit-on=FAILURE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      INVOKE 'invokeUpdateVendorInXLink'
        service: GLDExpressGateway.ProcessFlows.VMR:invokeUpdateVendorInXLink
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeGetVendorDetailsByGldId'
        service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on '/AppSubmitRequest/SBSRequest/AppSubmitRequest/TermRequested'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
LOOP over '?'
  MAP [mode=STANDALONE]
  END-MAP
END-LOOP
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/SubmitToCredit'
  SEQUENCE 'false' exit-on=FAILURE
    BRANCH on ''
      SEQUENCE 'StatusUpdateID&gt;0' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        INVOKE 'invokeXML_SOAP'
          service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/invokeXosGenericXmlTransactionSave_1`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
BRANCH on ''
  SEQUENCE '$null' exit-on=FAILURE
    INVOKE 'getXLinkApplicantId'
      service: GLDExpressGateway.ProcessFlows.Applicant:getXLinkApplicantId
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
INVOKE 'invokeXML_SOAP'
  service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/processScreenButtonPerms`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/TAMGroups'
END-BRANCH
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
LOOP over '?'
  BRANCH on ''
    SEQUENCE '%GroupList%='efw' or %GroupList%='EFW'' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
  END-SEQUENCE
END-BRANCH
LOOP over '?'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  LOOP over '?'
    BRANCH on ''
      SEQUENCE '%GroupList%=%GroupPermission%' exit-on=FAILURE
        BRANCH on '/size'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'appendToStringList'
              service: pub.list:appendToStringList
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          LOOP over '?'
            BRANCH on ''
              SEQUENCE '%curPermission%=%Permissions%' exit-on=FAILURE
                MAP [mode=STANDALONE]
                END-MAP
              END-SEQUENCE
            END-BRANCH
          END-LOOP
        END-BRANCH
        BRANCH on '/addToList'
          INVOKE 'true'
            service: pub.list:appendToStringList
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-BRANCH
      END-SEQUENCE
    END-BRANCH
  END-LOOP
END-LOOP
END-LOOP
LOOP over '?'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-LOOP
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'xmlStringToXMLNode'
    service: pub.xml:xmlStringToXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'xmlNodeToDocument'
    service: pub.xml:xmlNodeToDocument
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?'
    BRANCH on ''
      INVOKE '%/SBSResponse/SBSResponse/LoginResponse/PermissionList/Permission/@category%!=5001'
        service: pub.list:appendToDocumentList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-BRANCH
  END-LOOP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'appendToDocumentList'
    service: pub.list:appendToDocumentList
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/ProcessFlows/publishSubmitToCredit`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
INVOKE 'publish'
  service: pub.publish:publish
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/ProcessFlows/setAppSubmitAssets`

```
LOOP over '?'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  RETRY max=%count%
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'appendToDocumentList'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-RETRY
  MAP [mode=STANDALONE]
  END-MAP
END-LOOP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/ProcessFlows/setGroups`

```
BRANCH on '/LoginRequest/SBSRequest/LoginRequest/User/LoginName'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDExpressGateway/Utilities/FlowServices/EFW/isTransactionApproved`

```
INVOKE 'getGldTranStatusCategory'
  service: GLDExpressGateway.Utilities.FlowServices:getGldTranStatusCategory
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on ''
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
INVOKE 'clearPipeline'
  service: pub.flow:clearPipeline
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/Utilities/FlowServices/String/getTrimmedSubstring`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/variables/endIndex'
  SEQUENCE '-1' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
END-SEQUENCE
SEQUENCE '$default' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
END-BRANCH
```

### `GLDExpressGateway/Utilities/FlowServices/clenseXLinkDate`

```
BRANCH on '/date'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  SEQUENCE '$default' exit-on=FAILURE
    INVOKE 'getXLinkConstants'
      service: GLDExpressGateway.Utilities.FlowServices:getXLinkConstants
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'dateTimeFormat'
      service: pub.date:dateTimeFormat
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-BRANCH
```

### `GLDExpressGateway/Utilities/FlowServices/getDandBConstants`

```
INVOKE 'getTNProfile'
  service: GLDExpressGateway.Utilities.FlowServices:getTNProfile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/ConstantName'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/getDateDiff`

```
BRANCH on '/startDateFormat'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-BRANCH
INVOKE 'calculateDateDifference'
  service: GLDExpressGateway.Utilities.JavaServices:calculateDateDifference
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/Utilities/FlowServices/getDocument`

```
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/Utilities/FlowServices/getELBusinessType`

```
MAP [mode=STANDALONE]
END-MAP
BRANCH on '/returnValueType'
  SEQUENCE 'EFWBusinessType' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on '/returnValue'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
  END-SEQUENCE
  SEQUENCE 'BusinessType' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on '/returnValue'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
  END-SEQUENCE
  SEQUENCE 'TypeOfCustomer' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on '/returnValue'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on '/returnValue'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-BRANCH
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/getEfwServiceNameToInvoke`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'savePipelineToFile' [DISABLED]
  service: pub.flow:savePipelineToFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'restorePipelineFromFile' [DISABLED]
  service: pub.flow:restorePipelineFromFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'getTrimmedSubstring'
    service: GLDExpressGateway.Utilities.FlowServices.String:getTrimmedSubstring
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/tempAppData/endAppIdIndex'
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      BRANCH on ''
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
      BRANCH on '/operands/isAppDataRequestForGld'
        SEQUENCE 'true' exit-on=FAILURE
          INVOKE 'getTrimmedSubstring'
            service: GLDExpressGateway.Utilities.FlowServices.String:getTrimmedSubstring
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on '/tempAppData/endUserIdIndex'
        END-BRANCH
        INVOKE 'invokeGetTransactionDetails'
          service: GLDExpressGateway.ProcessFlows:invokeGetTransactionDetails
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'invokeGetVendorDetailsByGldId'
          service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'invokeUserSourcePermissionCheckRequest'
          service: GLDExpressGateway.ProcessFlows.EFW:invokeUserSourcePermissionCheckRequest
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/tempAppData/userHasSourcePermission'
          SEQUENCE 'true' exit-on=FAILURE
          END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
    SEQUENCE 'false' exit-on=FAILURE
    END-SEQUENCE
  END-BRANCH
  SEQUENCE '' exit-on=FAILURE [DISABLED]
    INVOKE 'getTrimmedSubstring' [DISABLED]
      service: GLDExpressGateway.Utilities.FlowServices.String:getTrimmedSubstring
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/tempAppData/endSecondAppIdIndex' [DISABLED]
      SEQUENCE '-1' exit-on=FAILURE [DISABLED]
        MAP [mode=STANDALONE] [DISABLED]
        END-MAP
        MAP [mode=STANDALONE] [DISABLED]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        BRANCH on '' [DISABLED]
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
        END-BRANCH
        BRANCH on '/operands/isAppDataRequestForGld' [DISABLED]
          SEQUENCE 'true' exit-on=FAILURE [DISABLED]
            INVOKE 'getTrimmedSubstring' [DISABLED]
              service: GLDExpressGateway.Utilities.FlowServices.String:getTrimmedSubstring
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            BRANCH on '/tempAppData/endUserIdIndex' [DISABLED]
          END-BRANCH
          INVOKE 'invokeGetTransactionDetails' [DISABLED]
            service: GLDExpressGateway.ProcessFlows:invokeGetTransactionDetails
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'invokeGetVendorDetailsByGldId' [DISABLED]
            service: GLDExpressGateway.ProcessFlows.VMR:invokeGetVendorDetailsByGldId
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'invokeUserSourcePermissionCheckRequest' [DISABLED]
            service: GLDExpressGateway.ProcessFlows.EFW:invokeUserSourcePermissionCheckRequest
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on '/tempAppData/userHasSourcePermission' [DISABLED]
            SEQUENCE 'true' exit-on=FAILURE [DISABLED]
            END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
      SEQUENCE 'false' exit-on=FAILURE [DISABLED]
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
END-BRANCH
END-SEQUENCE
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'getServiceName'
    service: GLDExpressGateway.Utilities.FlowServices:getServiceName
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'serviceExists'
    service: GLDExpressGateway.Utilities.JavaServices:serviceExists
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/efwRequestName'
    SEQUENCE 'RefDataRequest' exit-on=FAILURE
      INVOKE 'xmlNodeToDocument'
        service: pub.xml:xmlNodeToDocument
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/RefDataRequest/SBSRequest/RefDataRequest/@type'
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on ''
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on ''
    SEQUENCE 'userIsExpressLink == &quot;true&quot; &amp;&amp; serviceExists == &quot;True&quot;' exit-on=FAILURE
      BRANCH on '/isRequestForAppData'
        MAP [mode=STANDALONE]
        END-MAP
        BRANCH on '/isAppDataRequestForGld'
          MAP [mode=STANDALONE]
          END-MAP
          MAP [mode=STANDALONE]
          END-MAP
        END-BRANCH
      END-BRANCH
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
INVOKE 'clearPipeline'
  service: pub.flow:clearPipeline
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/Utilities/FlowServices/getEfwServiceNameToInvoke_9_10_08_pre_appid_logic`

```
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'getServiceName'
    service: GLDExpressGateway.Utilities.FlowServices:getServiceName
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'serviceExists'
    service: GLDExpressGateway.Utilities.JavaServices:serviceExists
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/efwRequestName'
    SEQUENCE 'RefDataRequest' exit-on=FAILURE
      INVOKE 'xmlNodeToDocument'
        service: pub.xml:xmlNodeToDocument
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/RefDataRequest/SBSRequest/RefDataRequest/@type'
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on ''
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on ''
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-BRANCH
END-SEQUENCE
INVOKE 'clearPipeline'
  service: pub.flow:clearPipeline
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/Utilities/FlowServices/getEfwServiceNameToInvoke_9_11_08_pre_data_perm`

```
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '/tempAppData/appIdStartIndex'
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE '$default' exit-on=FAILURE
      SEQUENCE '' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        BRANCH on '/tempAppData/appIdSecondStartIndex'
          SEQUENCE '-1' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            BRANCH on ''
              MAP [mode=STANDALONE]
              END-MAP
              MAP [mode=STANDALONE]
              END-MAP
              MAP [mode=STANDALONE]
              END-MAP
            END-BRANCH
            BRANCH on '/operands/isAppDataRequestForGld' [DISABLED]
              SEQUENCE 'true' exit-on=FAILURE [DISABLED]
              END-SEQUENCE
              SEQUENCE 'false' exit-on=FAILURE [DISABLED]
              END-SEQUENCE
            END-BRANCH
          END-SEQUENCE
          MAP [mode=STANDALONE]
          END-MAP
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'getServiceName'
    service: GLDExpressGateway.Utilities.FlowServices:getServiceName
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'serviceExists'
    service: GLDExpressGateway.Utilities.JavaServices:serviceExists
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/efwRequestName'
    SEQUENCE 'RefDataRequest' exit-on=FAILURE
      INVOKE 'xmlNodeToDocument'
        service: pub.xml:xmlNodeToDocument
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/RefDataRequest/SBSRequest/RefDataRequest/@type'
        MAP [mode=STANDALONE]
        END-MAP
      END-BRANCH
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on ''
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  BRANCH on ''
    SEQUENCE 'userIsExpressLink == &quot;true&quot; &amp;&amp; serviceExists == &quot;True&quot;' exit-on=FAILURE
      BRANCH on '/isRequestForAppData'
        MAP [mode=STANDALONE]
        END-MAP
        BRANCH on '/isAppDataRequestForGld'
          MAP [mode=STANDALONE]
          END-MAP
          MAP [mode=STANDALONE]
          END-MAP
        END-BRANCH
      END-BRANCH
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
INVOKE 'clearPipeline'
  service: pub.flow:clearPipeline
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressGateway/Utilities/FlowServices/getGldStatusIdList`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/getGldTranStatusCategory`

```
MAP [mode=STANDALONE]
END-MAP
BRANCH on '/returnValue'
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/getNextSequenceValue`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'registerStore'
  service: pub.storage:registerStore
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'get'
  service: pub.storage:get
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/sequenceStarted'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-BRANCH
INVOKE 'put'
  service: pub.storage:put
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/lengthLimit'
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on '/prefixLength'
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/getRelatedPartyType`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/typeId'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/Utilities/FlowServices/getServiceName`

```
SEQUENCE '' exit-on=DONE
  INVOKE 'queryXMLNode'
    service: pub.xml:queryXMLNode
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on '/service'
    SEQUENCE '$null' exit-on=FAILURE
      INVOKE 'getXMLNodeIterator'
        service: pub.xml:getXMLNodeIterator
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'getNextXMLNode'
        service: pub.xml:getNextXMLNode
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'getXMLNodeIterator'
        service: pub.xml:getXMLNodeIterator
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'getNextXMLNode'
        service: pub.xml:getNextXMLNode
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/Utilities/FlowServices/getTNProfile`

```
SEQUENCE '' exit-on=FAILURE
  INVOKE 'getInternalID'
    service: wm.tn.profile:getInternalID
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'getProfile'
    service: wm.tn.profile:getProfile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  LOOP over '?'
    BRANCH on '/profile/Delivery/Protocol'
      BRANCH on ''
        SEQUENCE '%profile/Delivery/PrimaryAddr/MBoolean% =true' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
      END-BRANCH
      BRANCH on ''
        SEQUENCE '%profile/Delivery/PrimaryAddr/MBoolean% =true' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          BRANCH on '/invoke'
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            MAP [mode=STANDALONE]
            END-MAP
          END-BRANCH
        END-SEQUENCE
      END-BRANCH
      BRANCH on ''
        SEQUENCE '%profile/Delivery/PrimaryAddr/MBoolean% =true' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
      END-BRANCH
    END-BRANCH
  END-LOOP
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/getVMSMTConstants`

```
BRANCH on '/ConstantName'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/getVMSMTUserConstants`

```
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on ''
  SEQUENCE 'result='true'' exit-on=FAILURE
    INVOKE 'getVMSMTConstants'
      service: GLDExpressGateway.Utilities.FlowServices:getVMSMTConstants
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on ''
  SEQUENCE 'result='true'' exit-on=FAILURE
    INVOKE 'getVMSMTConstants'
      service: GLDExpressGateway.Utilities.FlowServices:getVMSMTConstants
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on ''
  SEQUENCE 'result='true'' exit-on=FAILURE
    INVOKE 'getVMSMTConstants'
      service: GLDExpressGateway.Utilities.FlowServices:getVMSMTConstants
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
```

### `GLDExpressGateway/Utilities/FlowServices/getWmForXLinkUserId`

```
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/getXLinkConstants`

```
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
END-SEQUENCE
```

### `GLDExpressGateway/Utilities/FlowServices/getXLinkConstants_9_24`

```
BRANCH on '/ConstantName'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDExpressGateway/Utilities/FlowServices/invokeCheckWriter`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getTNProfile'
      service: GLDExpressGateway.Utilities.FlowServices:getTNProfile
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    INVOKE 'http'
      service: pub.client:http
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'ByteArrayToString'
      service: WmTransformationServices:ByteArrayToString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'logRequestResponse'
      service: GLDExpressGateway.Utilities.FlowServices:logRequestResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'http'
      service: pub.client:http
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'ByteArrayToString'
      service: WmTransformationServices:ByteArrayToString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'logRequestResponse'
      service: GLDExpressGateway.Utilities.FlowServices:logRequestResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressGateway/Utilities/FlowServices/invokeFindMatchInList`

```
BRANCH on '/MatchType'
  SEQUENCE 'ExactMatch' exit-on=FAILURE
    LOOP over '?'
      BRANCH on ''
        SEQUENCE '%List/Item%==%LookFor%' exit-on=FAILURE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
      END-SEQUENCE
    END-BRANCH
  END-LOOP
END-SEQUENCE
SEQUENCE 'SimilarMatch' exit-on=FAILURE
  LOOP over '?'
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on ''
      SEQUENCE 'MatchIndex &gt;= 0' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
    END-SEQUENCE
  END-BRANCH
END-LOOP
END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/invokeMatchVMR_ID_to_XLink_ID`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on ''
  SEQUENCE '%ID_Type%=&quot;SUPPLIER STATUS&quot;' exit-on=FAILURE
    BRANCH on ''
      SEQUENCE '%VMR_ID%=&quot;18&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '%VMR_ID%=&quot;16&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '%VMR_ID%=&quot;17&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '%VMR_ID%=&quot;15&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '%ID_Type%=&quot;VENDOR STATUS&quot;' exit-on=FAILURE
    BRANCH on ''
      SEQUENCE '%VMR_ID%=&quot;18&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '%VMR_ID%=&quot;16&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '%VMR_ID%=&quot;17&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '%VMR_ID%=&quot;15&quot;' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/invokeXML_HTTP`

```
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=DONE
  INVOKE 'LogXMLRequest'
    service: GLDMessageLog:LogXMLRequest
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'getTNProfile'
  service: GLDExpressGateway.Utilities.FlowServices:getTNProfile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'http'
  service: pub.client:http
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/status'
  SEQUENCE '200' exit-on=FAILURE
    INVOKE 'ByteArrayToString'
      service: WmTransformationServices:ByteArrayToString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
END-SEQUENCE
END-BRANCH
```

### `GLDExpressGateway/Utilities/FlowServices/invokeXML_SOAP`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getTNProfile'
      service: GLDExpressGateway.Utilities.FlowServices:getTNProfile
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'concat'
      service: pub.string:concat
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/nameSpace'
      SEQUENCE '$null' exit-on=FAILURE
        INVOKE 'invokeSOAPService'
          service: GLDSoap.ProcessFlows:invokeSOAPService
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        INVOKE 'invokeSOAPService'
          service: GLDSoap.ProcessFlows:invokeSOAPService
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
    SEQUENCE '' exit-on=DONE
      BRANCH on ''
        SEQUENCE 'SOAP-FAULT/faultcode!=$null' exit-on=DONE
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
          INVOKE 'LogXMLResponse'
            service: GLDMessageLog:LogXMLResponse
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
      END-SEQUENCE
    END-BRANCH
    INVOKE 'LogXMLResponse'
      service: GLDMessageLog:LogXMLResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'LogXMLResponse'
    service: GLDMessageLog:LogXMLResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/invokeXML_SOAP_1`

```
INVOKE 'savePipelineToFile' [DISABLED]
  service: pub.flow:savePipelineToFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'restorePipelineFromFile' [DISABLED]
  service: pub.flow:restorePipelineFromFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    INVOKE 'getTNProfile'
      service: GLDExpressGateway.Utilities.FlowServices:getTNProfile
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'concat'
      service: pub.string:concat
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'invokeSOAPService'
      service: GLDSoap.ProcessFlows:invokeSOAPService
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLResponse'
        service: GLDMessageLog:LogXMLResponse
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
END-SEQUENCE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/isNullOrBlank`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/outString'
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDExpressGateway/Utilities/FlowServices/isUserAssignedGLDgroups`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on ''
  SEQUENCE 'efwUserIndex &gt;= 0' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    BRANCH on ''
      SEQUENCE 'efw3rdPartyUser &gt;= 0' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/Utilities/FlowServices/logRequestResponse`

```
SEQUENCE '' exit-on=DONE
  INVOKE 'LogXMLRequest'
    service: GLDMessageLog:LogXMLRequest
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'LogXMLResponse'
    service: GLDMessageLog:LogXMLResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
```

### `GLDExpressGateway/Utilities/FlowServices/lookupCountryFromProvince`

```
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/countryCode'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
```

### `GLDExpressGateway/Utilities/FlowServices/lookupCustomFieldIdBasedOnName`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/customFieldId'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressGateway/WebConnectors/DNB_x0020_US_x0020_Commercial_x0020_Credit_x0020_BureauSoap/GetEM09LookupResponse`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/_port'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  BRANCH on '/binding'
    SEQUENCE 'SOAP_MSG' exit-on=FAILURE
      INVOKE 'createSoapData'
        service: pub.soap.utils:createSoapData
        MAP [mode=INPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addBodyEntry'
            service: pub.soap.utils:addBodyEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'soapHTTP'
          service: pub.client:soapHTTP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/soapStatus'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'getBody'
              service: pub.soap.utils:getBody
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE '1' exit-on=FAILURE
            INVOKE 'getBodyEntries'
              service: pub.soap.utils:getBodyEntries
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/WebConnectors/DNB_x0020_US_x0020_Commercial_x0020_Credit_x0020_BureauSoap/GetListOfSimilars`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/_port'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  BRANCH on '/binding'
    SEQUENCE 'SOAP_MSG' exit-on=FAILURE
      INVOKE 'createSoapData'
        service: pub.soap.utils:createSoapData
        MAP [mode=INPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addBodyEntry'
            service: pub.soap.utils:addBodyEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          MAP [mode=STANDALONE]
          END-MAP
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addHeaderEntry'
            service: pub.soap.utils:addHeaderEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'soapHTTP'
          service: pub.client:soapHTTP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/soapStatus'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'getBody'
              service: pub.soap.utils:getBody
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE '1' exit-on=FAILURE
            INVOKE 'getBodyEntries'
              service: pub.soap.utils:getBodyEntries
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/WebConnectors/DNB_x0020_US_x0020_Commercial_x0020_Credit_x0020_BureauSoap/GetListOfSimilarsHtml`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/_port'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  BRANCH on '/binding'
    SEQUENCE 'SOAP_MSG' exit-on=FAILURE
      INVOKE 'createSoapData'
        service: pub.soap.utils:createSoapData
        MAP [mode=INPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addBodyEntry'
            service: pub.soap.utils:addBodyEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'soapHTTP'
          service: pub.client:soapHTTP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/soapStatus'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'getBody'
              service: pub.soap.utils:getBody
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE '1' exit-on=FAILURE
            INVOKE 'getBodyEntries'
              service: pub.soap.utils:getBodyEntries
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/WebConnectors/DNB_x0020_US_x0020_Commercial_x0020_Credit_x0020_BureauSoap/GetListOfSimilarsXml`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/_port'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  BRANCH on '/binding'
    SEQUENCE 'SOAP_MSG' exit-on=FAILURE
      INVOKE 'createSoapData'
        service: pub.soap.utils:createSoapData
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          INVOKE 'stringToSoapData'
            service: pub.soap.utils:stringToSoapData
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          MAP [mode=STANDALONE] [DISABLED]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          INVOKE 'xmlStringToXMLNode' [DISABLED]
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode' [DISABLED]
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode' [DISABLED]
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addBodyEntry' [DISABLED]
            service: pub.soap.utils:addBodyEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode' [DISABLED]
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addHeaderEntry' [DISABLED]
            service: pub.soap.utils:addHeaderEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
          INVOKE 'stringToSoapData' [DISABLED]
            service: pub.soap.utils:stringToSoapData
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'soapHTTP'
          service: pub.client:soapHTTP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/soapStatus'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'getBody'
              service: pub.soap.utils:getBody
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE '1' exit-on=FAILURE
            INVOKE 'getBodyEntries'
              service: pub.soap.utils:getBodyEntries
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/WebConnectors/DNB_x0020_US_x0020_Commercial_x0020_Credit_x0020_BureauSoap/GetPacket`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/_port'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  BRANCH on '/binding'
    SEQUENCE 'SOAP_MSG' exit-on=FAILURE
      INVOKE 'createSoapData'
        service: pub.soap.utils:createSoapData
        MAP [mode=INPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addBodyEntry'
            service: pub.soap.utils:addBodyEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'soapHTTP'
          service: pub.client:soapHTTP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/soapStatus'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'getBody'
              service: pub.soap.utils:getBody
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE '1' exit-on=FAILURE
            INVOKE 'getBodyEntries'
              service: pub.soap.utils:getBodyEntries
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/WebConnectors/DNB_x0020_US_x0020_Commercial_x0020_Credit_x0020_BureauSoap/GetPacketsFromArf`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/_port'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  BRANCH on '/binding'
    SEQUENCE 'SOAP_MSG' exit-on=FAILURE
      INVOKE 'createSoapData'
        service: pub.soap.utils:createSoapData
        MAP [mode=INPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addBodyEntry'
            service: pub.soap.utils:addBodyEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'soapHTTP'
          service: pub.client:soapHTTP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/soapStatus'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'getBody'
              service: pub.soap.utils:getBody
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE '1' exit-on=FAILURE
            INVOKE 'getBodyEntries'
              service: pub.soap.utils:getBodyEntries
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

### `GLDExpressGateway/WebConnectors/DNB_x0020_US_x0020_Commercial_x0020_Credit_x0020_BureauSoap/GetReport`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/_port'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  BRANCH on '/binding'
    SEQUENCE 'SOAP_MSG' exit-on=FAILURE
      INVOKE 'createSoapData'
        service: pub.soap.utils:createSoapData
        MAP [mode=INPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addBodyEntry'
            service: pub.soap.utils:addBodyEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'soapHTTP'
          service: pub.client:soapHTTP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/soapStatus'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'getBody'
              service: pub.soap.utils:getBody
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE '1' exit-on=FAILURE
            INVOKE 'getBodyEntries'
              service: pub.soap.utils:getBodyEntries
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

## Package: GLDExpressWebServices

### `GLDExpressWebServices/MainFlows/Example`

```
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressWebServices/MainFlows/NormalizeAddress`

```
BRANCH on '/debug'
  INVOKE '$null'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
INVOKE 'appendToDocumentList'
  service: pub.list:appendToDocumentList
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
INVOKE 'appendToDocumentList'
  service: pub.list:appendToDocumentList
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/MainFlows/approvedStatusChangeNotification`

```
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressWebServices/MainFlows/genericStatusChangeNotification`

```
BRANCH on '/debug'
  INVOKE '$null'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'documentToXMLString'
        service: pub.xml:documentToXMLString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'documentToXMLString'
        service: pub.xml:documentToXMLString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      INVOKE 'trim'
        service: pub.string:trim
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      BRANCH on '/genericStatusChangeRequest/ns1:genericStatusChangeWrapper/statusID'
        SEQUENCE '48' exit-on=FAILURE
          MAP [mode=STANDALONE] [DISABLED]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
          END-MAP
          SEQUENCE '' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
          SEQUENCE '' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      SEQUENCE '' exit-on=FAILURE
        LOOP over '?'
          MAP [mode=STANDALONE]
          END-MAP
          INVOKE 'appendToDocumentList'
            service: pub.list:appendToDocumentList
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-LOOP
        LOOP over '?'
          MAP [mode=STANDALONE]
          END-MAP
          INVOKE 'appendToDocumentList'
            service: pub.list:appendToDocumentList
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-LOOP
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      MAP [mode=STANDALONE] [DISABLED]
      END-MAP
      INVOKE 'documentToXMLString'
        service: pub.xml:documentToXMLString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeXML_HTTP'
        service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'xmlStringToXMLNode'
        service: pub.xml:xmlStringToXMLNode
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'xmlNodeToDocument'
        service: pub.xml:xmlNodeToDocument
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'appendToStringList'
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      LOOP over '?'
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'appendToStringList'
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      INVOKE 'appendToStringList'
        service: pub.list:appendToStringList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'makeString'
        service: pub.string:makeString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'appendToStringList'
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      INVOKE 'makeString'
        service: pub.string:makeString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      SEQUENCE '%vendorEmailAddressString% != $null &amp;&amp; %vendorEmailAddressString% != ''' exit-on=FAILURE
        INVOKE 'concat'
          service: pub.string:concat
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    BRANCH on ''
      SEQUENCE '%kefEmailAddressString% != $null &amp;&amp; %kefEmailAddressString% != ''' exit-on=FAILURE
        BRANCH on ''
          SEQUENCE '%emailAddressString% != ''' exit-on=FAILURE
            INVOKE 'concat'
              service: pub.string:concat
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'concat'
              service: pub.string:concat
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            INVOKE 'concat'
              service: pub.string:concat
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    SEQUENCE '' exit-on=FAILURE [DISABLED]
      MAP [mode=STANDALONE] [DISABLED]
      END-MAP
      BRANCH on '' [DISABLED]
        INVOKE '%emailAddressString%!=null and %emailAddressString%!=&quot;&quot;' [DISABLED]
          service: pub.string:concat
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-BRANCH
      MAP [mode=STANDALONE] [DISABLED]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
    BRANCH on ''
      SEQUENCE '%emailAddressString% != ''' exit-on=FAILURE
        INVOKE 'replace'
          service: pub.string:replace
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'invokeXML_SOAP'
          service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'setResponse'
      service: pub.flow:setResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'currentDate'
      service: pub.date:currentDate
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getDebugInfo'
      service: WSRProcessStatistics.ProcessFlows:getDebugInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/DebugInfo/EFW'
      SEQUENCE '/.+/' exit-on=FAILURE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        INVOKE 'publishStatsDoc'
          service: WSRProcessStatistics.MainFlows:publishStatsDoc
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
    INVOKE 'getDebugInfo'
      service: WSRProcessStatistics.ProcessFlows:getDebugInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on ''
      SEQUENCE '%DebugInfo/GLDRealTime% != false or %DebugInfo/GLDRealTime% = $null' exit-on=FAILURE
        INVOKE 'getServiceName'
          service: WSRCommon.Utilities.JavaServices:getServiceName
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'publishStatsDoc'
          service: WSRProcessStatistics.MainFlows:publishStatsDoc
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'clearPipeline'
      service: pub.flow:clearPipeline
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'publishErrorDoc'
    service: WSRProcessStatistics.MainFlows:publishErrorDoc
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'setResponse'
    service: pub.flow:setResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'clearPipeline'
    service: pub.flow:clearPipeline
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressWebServices/MainFlows/genericStatusChangeNotification_SOAPUI`

```
BRANCH on '/debug'
  INVOKE '$null'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'currentDate'
      service: pub.date:currentDate
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      MAP [mode=STANDALONE] [DISABLED]
      END-MAP
      INVOKE 'xmlStringToXMLNode' [DISABLED]
        service: pub.xml:xmlStringToXMLNode
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'xmlNodeToDocument' [DISABLED]
        service: pub.xml:xmlNodeToDocument
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
      END-MAP
      SEQUENCE '' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
      INVOKE 'documentToXMLString'
        service: pub.xml:documentToXMLString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
      INVOKE 'documentToXMLString'
        service: pub.xml:documentToXMLString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      INVOKE 'trim'
        service: pub.string:trim
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      BRANCH on '/genericStatusChangeRequest/ns1:genericStatusChangeWrapper/statusID'
        SEQUENCE '48' exit-on=FAILURE
          MAP [mode=STANDALONE] [DISABLED]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          MAP [mode=STANDALONE]
          END-MAP
          SEQUENCE '' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
          SEQUENCE '' exit-on=FAILURE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      SEQUENCE '' exit-on=FAILURE
        LOOP over '?'
          MAP [mode=STANDALONE]
          END-MAP
          INVOKE 'appendToDocumentList'
            service: pub.list:appendToDocumentList
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-LOOP
        LOOP over '?'
          MAP [mode=STANDALONE]
          END-MAP
          INVOKE 'appendToDocumentList'
            service: pub.list:appendToDocumentList
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-LOOP
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      MAP [mode=STANDALONE] [DISABLED]
      END-MAP
      INVOKE 'documentToXMLString'
        service: pub.xml:documentToXMLString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'invokeXML_HTTP'
        service: GLDExpressGateway.Utilities.FlowServices:invokeXML_HTTP
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'xmlStringToXMLNode'
        service: pub.xml:xmlStringToXMLNode
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'xmlNodeToDocument'
        service: pub.xml:xmlNodeToDocument
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'appendToStringList'
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      LOOP over '?'
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'appendToStringList'
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      INVOKE 'appendToStringList'
        service: pub.list:appendToStringList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'makeString'
        service: pub.string:makeString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      LOOP over '?'
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'appendToStringList'
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      INVOKE 'makeString'
        service: pub.string:makeString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      SEQUENCE '%vendorEmailAddressString% != $null &amp;&amp; %vendorEmailAddressString% != ''' exit-on=FAILURE
        INVOKE 'concat'
          service: pub.string:concat
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
      END-SEQUENCE
    END-BRANCH
    BRANCH on ''
      SEQUENCE '%kefEmailAddressString% != $null &amp;&amp; %kefEmailAddressString% != ''' exit-on=FAILURE
        BRANCH on ''
          SEQUENCE '%emailAddressString% != ''' exit-on=FAILURE
            INVOKE 'concat'
              service: pub.string:concat
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'concat'
              service: pub.string:concat
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            INVOKE 'concat'
              service: pub.string:concat
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
      END-SEQUENCE
    END-BRANCH
    SEQUENCE '' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
    BRANCH on ''
      SEQUENCE '%emailAddressString% != ''' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE [DISABLED]
          MAP [mode=STANDALONE] [DISABLED]
          END-MAP
          MAP [mode=STANDALONE] [DISABLED]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-SEQUENCE
        INVOKE 'replace'
          service: pub.string:replace
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
        INVOKE 'invokeXML_SOAP'
          service: GLDExpressGateway.Utilities.FlowServices:invokeXML_SOAP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '$default' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    SEQUENCE '' exit-on=FAILURE [DISABLED]
      LOOP over '?' [DISABLED]
        MAP [mode=STANDALONE] [DISABLED]
        END-MAP
        INVOKE 'appendToStringList' [DISABLED]
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      LOOP over '?' [DISABLED]
        MAP [mode=STANDALONE] [DISABLED]
        END-MAP
        INVOKE 'appendToStringList' [DISABLED]
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      INVOKE 'appendToStringList' [DISABLED]
        service: pub.list:appendToStringList
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'makeString' [DISABLED]
        service: pub.string:makeString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      LOOP over '?' [DISABLED]
        MAP [mode=STANDALONE] [DISABLED]
        END-MAP
        INVOKE 'appendToStringList' [DISABLED]
          service: pub.list:appendToStringList
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-LOOP
      INVOKE 'makeString' [DISABLED]
        service: pub.string:makeString
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE] [DISABLED]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE] [DISABLED]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
    INVOKE 'currentDate'
      service: pub.date:currentDate
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'documentToXMLString'
      service: pub.xml:documentToXMLString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'setResponse'
      service: pub.flow:setResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getDebugInfo'
      service: WSRProcessStatistics.ProcessFlows:getDebugInfo
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on ''
      SEQUENCE '%DebugInfo/GLDRealTime% != false or %DebugInfo/GLDRealTime% = $null' exit-on=FAILURE
        INVOKE 'getServiceName'
          service: WSRCommon.Utilities.JavaServices:getServiceName
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'publishStatsDoc'
          service: WSRProcessStatistics.MainFlows:publishStatsDoc
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-BRANCH
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'clearPipeline'
      service: pub.flow:clearPipeline
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'publishErrorDoc'
    service: WSRProcessStatistics.MainFlows:publishErrorDoc
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'documentToXMLString'
    service: pub.xml:documentToXMLString
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'setResponse'
    service: pub.flow:setResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'clearPipeline'
    service: pub.flow:clearPipeline
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressWebServices/MainFlows/getLesseeIDFromLPK`

```
BRANCH on '/debug'
  INVOKE '$default'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'getStateCode'
        service: GLDExpressWebServices.Utilities.FlowServices:getStateCode
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'checkDocument'
        service: GLDExpressWebServices.ProcessFlows.GetLesseeIDFromLPK:checkDocument
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/isNullOrBlank'
        SEQUENCE 'true' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
        SEQUENCE 'false' exit-on=FAILURE
          SEQUENCE '' exit-on=SUCCESS
            SEQUENCE '' exit-on=FAILURE
              MAP [mode=STANDALONE]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
              MAP [mode=STANDALONE]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
              INVOKE 'getLesseeRecordsFromLPKDirectFromCartman'
                service: GLDExpressAdapterServices.LeasePak:getLesseeRecordsFromLPKDirectFromCartman
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
              INVOKE 'getLesseeRecordsFromLPK' [DISABLED]
                service: GLDExpressAdapterServices.LeasePak:getLesseeRecordsFromLPK
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
            END-SEQUENCE
            SEQUENCE '' exit-on=DONE
              MAP [mode=STANDALONE]
              END-MAP
          END-SEQUENCE
        END-SEQUENCE
        SEQUENCE '' exit-on=FAILURE
          LOOP over '?'
            MAP [mode=STANDALONE]
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
              MAP [mode=INVOKEINPUT]
              END-MAP
              MAP [mode=INVOKEOUTPUT]
              END-MAP
            END-MAP
            MAP [mode=STANDALONE]
            END-MAP
            BRANCH on ''
              SEQUENCE '%trimmedCustomerNumber% =  %dbCustomerNumber%' exit-on=FAILURE
                MAP [mode=STANDALONE]
                END-MAP
                INVOKE 'doesLesseeMatch'
                  service: GLDExpressWebServices.Utilities.JavaServices:doesLesseeMatch
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
                BRANCH on '/matched'
                  SEQUENCE 'true' exit-on=FAILURE
                    MAP [mode=STANDALONE]
                    END-MAP
                    INVOKE 'appendToStringList'
                      service: pub.list:appendToStringList
                      MAP [mode=INPUT]
                      END-MAP
                      MAP [mode=OUTPUT]
                      END-MAP
                    END-INVOKE
                  END-SEQUENCE
                  SEQUENCE 'false' exit-on=FAILURE
                    MAP [mode=STANDALONE]
                    END-MAP
                  END-SEQUENCE
                END-BRANCH
              END-SEQUENCE
            END-BRANCH
          END-LOOP
          SEQUENCE '' exit-on=FAILURE
            INVOKE 'sizeOfList'
              service: pub.list:sizeOfList
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            BRANCH on ''
              SEQUENCE '%sizeOfLesseeIDList% &gt; 0' exit-on=FAILURE
                MAP [mode=STANDALONE]
                END-MAP
              END-SEQUENCE
              SEQUENCE '$default' exit-on=FAILURE
                INVOKE 'getNextSequenceValue'
                  service: GLDExpressGateway.Utilities.FlowServices:getNextSequenceValue
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
              END-SEQUENCE
            END-BRANCH
          END-SEQUENCE
        END-SEQUENCE
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  INVOKE 'currentDate'
    service: pub.date:currentDate
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'publishErrorDoc'
    service: WSRProcessStatistics.MainFlows:publishErrorDoc
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'clearPipeline'
    service: pub.flow:clearPipeline
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  SEQUENCE '' exit-on=DONE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'publishErrorDoc'
    service: WSRProcessStatistics.MainFlows:publishErrorDoc
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
```

### `GLDExpressWebServices/MainFlows/processCustomerHistoryRequest`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getSystemTime'
      service: WSRProcessStatistics.ProcessFlows:getSystemTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getServiceName'
      service: WSRCommon.Utilities.JavaServices:getServiceName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    BRANCH on ''
      SEQUENCE '%getCustomerHistoryWrapperInput/ns1:getCustomerHistoryWrapper/customerID% == $null' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '%getCustomerHistoryWrapperInput/ns1:getCustomerHistoryWrapper/customerID% == ''' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    BRANCH on ''
      SEQUENCE '%responseErrorCode% &gt; 0' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  INVOKE 'selectCustomerHistory'
    service: GLDExpressAdapterServices.Customer:selectCustomerHistory
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on ''
    SEQUENCE '%selectCustomerHistoryOutput/results[0]/CUST_ID% == $null' exit-on=FAILURE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      BRANCH on ''
        SEQUENCE '%getCustomerHistoryWrapperInput/ns1:getCustomerHistoryWrapper/parentID% == $null' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
        SEQUENCE '%getCustomerHistoryWrapperInput/ns1:getCustomerHistoryWrapper/parentID% == ''' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'selectCustomerHistory'
            service: GLDExpressAdapterServices.Customer:selectCustomerHistory
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on ''
            SEQUENCE '%selectCustomerHistoryOutput/results[0]/CUST_ID% == $null' exit-on=FAILURE
              MAP [mode=STANDALONE]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
              MAP [mode=STANDALONE]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
              MAP [mode=STANDALONE]
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
                MAP [mode=INVOKEINPUT]
                END-MAP
                MAP [mode=INVOKEOUTPUT]
                END-MAP
              END-MAP
              MAP [mode=STANDALONE]
              END-MAP
            END-SEQUENCE
            SEQUENCE '$default' exit-on=FAILURE
              MAP [mode=STANDALONE]
              END-MAP
            END-SEQUENCE
          END-BRANCH
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
  END-MAP
  BRANCH on ''
    SEQUENCE '%lastError% == 'T'' exit-on=FAILURE
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
BRANCH on ''
  SEQUENCE '%currentCustomer% == %currentParent%' exit-on=FAILURE
END-SEQUENCE
END-BRANCH
RETRY max=
  INVOKE 'selectCustomerHistory'
    service: GLDExpressAdapterServices.Customer:selectCustomerHistory
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  BRANCH on ''
    SEQUENCE '%selectCustomerHistoryOutput/results[]/CUST_ID% == $null' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
    INVOKE 'appendToDocumentList'
      service: pub.list:appendToDocumentList
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
BRANCH on ''
  SEQUENCE '%currentCustomer% == %currentParent%' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
END-SEQUENCE
END-BRANCH
END-RETRY
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
  MAP [mode=STANDALONE]
  END-MAP
  SEQUENCE '' exit-on=DONE
    INVOKE 'LogXMLRequest'
      service: GLDMessageLog:LogXMLRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  INVOKE 'publishErrorDoc'
    service: WSRProcessStatistics.MainFlows:publishErrorDoc
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
END-SEQUENCE
```

### `GLDExpressWebServices/MainFlows/setTempCustomerHistoryOutput`

```
MAP [mode=STANDALONE]
END-MAP
BRANCH on '/customerHierarchyLevel'
  SEQUENCE '11' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '12' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '22' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '23' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '33' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '$default' exit-on=FAILURE
  END-SEQUENCE
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressWebServices/ProcessFlows/GetLesseeIDFromLPK/checkDocument`

```
MAP [mode=STANDALONE]
END-MAP
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/result'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/result'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/result'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/result'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/result'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/result'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
INVOKE 'isNullOrBlank'
  service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
BRANCH on '/result'
  SEQUENCE 'true' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
  END-SEQUENCE
  SEQUENCE 'false' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-BRANCH
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
```

### `GLDExpressWebServices/Utilities/FlowServices/getStateCode`

```
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
MAP [mode=STANDALONE]
  MAP [mode=INVOKEINPUT]
  END-MAP
  MAP [mode=INVOKEOUTPUT]
  END-MAP
END-MAP
BRANCH on '/stateCode'
  MAP [mode=STANDALONE]
  END-MAP
END-BRANCH
MAP [mode=STANDALONE]
END-MAP
```

### `GLDExpressWebServices/Wrappers/AddressNormalization/GLDExpressGatewayServices_AddressNormalizationPortType/normalizeAddress`

```
SEQUENCE '' exit-on=FAILURE
  BRANCH on '/_port'
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
  END-BRANCH
  BRANCH on '/binding'
    SEQUENCE 'SOAP_MSG' exit-on=FAILURE
      INVOKE 'createSoapData'
        service: pub.soap.utils:createSoapData
        MAP [mode=INPUT]
        END-MAP
      END-INVOKE
      SEQUENCE '' exit-on=FAILURE
        SEQUENCE '' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlStringToXMLNode'
            service: pub.xml:xmlStringToXMLNode
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'addBodyEntry'
            service: pub.soap.utils:addBodyEntry
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'soapHTTP'
          service: pub.client:soapHTTP
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on '/soapStatus'
          SEQUENCE '0' exit-on=FAILURE
            INVOKE 'getBody'
              service: pub.soap.utils:getBody
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            MAP [mode=STANDALONE]
            END-MAP
          END-SEQUENCE
          SEQUENCE '1' exit-on=FAILURE
            INVOKE 'getBodyEntries'
              service: pub.soap.utils:getBodyEntries
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlNodeToDocument'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
  END-BRANCH
END-SEQUENCE
```

### `GLDExpressWebServices/Wrappers/AddressNormalization/Registration/registerFlowServiceForSOAP`

```
INVOKE 'registerProcessor'
  service: pub.soap.processor:registerProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/AddressNormalization/Registration/unregisterFlowServiceForSOAP`

```
INVOKE 'unregisterProcessor'
  service: pub.soap.processor:unregisterProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/AddressNormalization/addressNormalizationWrapper`

```
INVOKE 'getBody'
  service: pub.soap.utils:getBody
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLRequest'
  service: GLDMessageLog:LogXMLRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'NormalizeAddress'
  service: GLDExpressWebServices.MainFlows:NormalizeAddress
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLResponse'
  service: GLDMessageLog:LogXMLResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'createSoapData'
  service: pub.soap.utils:createSoapData
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'addBodyEntry'
  service: pub.soap.utils:addBodyEntry
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/Example/Registration/registerFlowServiceForSOAP`

```
INVOKE 'registerProcessor'
  service: pub.soap.processor:registerProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/Example/Registration/unregisterFlowServiceForSOAP`

```
INVOKE 'unregisterProcessor'
  service: pub.soap.processor:unregisterProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/Example/exampleWrapper`

```
INVOKE 'getBody'
  service: pub.soap.utils:getBody
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLRequest'
  service: GLDMessageLog:LogXMLRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'Example'
  service: GLDExpressWebServices.MainFlows:Example
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLResponse'
  service: GLDMessageLog:LogXMLResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'createSoapData'
  service: pub.soap.utils:createSoapData
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'addBodyEntry'
  service: pub.soap.utils:addBodyEntry
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/GetCustomerHistory/Registration/registerFlowServiceForSOAP`

```
INVOKE 'registerProcessor'
  service: pub.soap.processor:registerProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/GetCustomerHistory/Registration/unregisterFlowServiceForSOAP`

```
INVOKE 'unregisterProcessor'
  service: pub.soap.processor:unregisterProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/GetCustomerHistory/getCustomerHistoryWrapper`

```
INVOKE 'getBody'
  service: pub.soap.utils:getBody
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLRequest'
  service: GLDMessageLog:LogXMLRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'processCustomerHistoryRequest'
  service: GLDExpressWebServices.MainFlows:processCustomerHistoryRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLResponse'
  service: GLDMessageLog:LogXMLResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'createSoapData'
  service: pub.soap.utils:createSoapData
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'addBodyEntry'
  service: pub.soap.utils:addBodyEntry
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/GetLesseeIDFromLPK/Registration/registerFlowServiceForSOAP`

```
INVOKE 'registerProcessor'
  service: pub.soap.processor:registerProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/GetLesseeIDFromLPK/Registration/unregisterFlowServiceForSOAP`

```
INVOKE 'unregisterProcessor'
  service: pub.soap.processor:unregisterProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/GetLesseeIDFromLPK/getLesseeIDFromLPKWrapper`

```
BRANCH on '/debug'
  INVOKE '$default'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
INVOKE 'getBody'
  service: pub.soap.utils:getBody
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLRequest'
  service: GLDMessageLog:LogXMLRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'getLesseeIDFromLPK'
  service: GLDExpressWebServices.MainFlows:getLesseeIDFromLPK
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLResponse'
  service: GLDMessageLog:LogXMLResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'createSoapData'
  service: pub.soap.utils:createSoapData
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'addBodyEntry'
  service: pub.soap.utils:addBodyEntry
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/StatusChangeNotification/Registration/registerFlowServiceForSOAP`

```
INVOKE 'registerProcessor'
  service: pub.soap.processor:registerProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'registerProcessor' [DISABLED]
  service: pub.soap.processor:registerProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/StatusChangeNotification/Registration/unregisterFlowServiceForSOAP`

```
INVOKE 'unregisterProcessor'
  service: pub.soap.processor:unregisterProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'unregisterProcessor' [DISABLED]
  service: pub.soap.processor:unregisterProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/StatusChangeNotification/approvedStatusChangeNotificationWrapper`

```
INVOKE 'getBody'
  service: pub.soap.utils:getBody
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLRequest'
  service: GLDMessageLog:LogXMLRequest
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'approvedStatusChangeNotification'
  service: GLDExpressWebServices.MainFlows:approvedStatusChangeNotification
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'LogXMLResponse'
  service: GLDMessageLog:LogXMLResponse
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'createSoapData'
  service: pub.soap.utils:createSoapData
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'addBodyEntry'
  service: pub.soap.utils:addBodyEntry
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDExpressWebServices/Wrappers/StatusChangeNotification/genericStatusChangeNotificationWrapper`

```
INVOKE 'getBody'
  service: pub.soap.utils:getBody
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=DONE
  INVOKE 'LogXMLRequest'
    service: GLDMessageLog:LogXMLRequest
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'genericStatusChangeNotification'
  service: GLDExpressWebServices.MainFlows:genericStatusChangeNotification
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=DONE
  INVOKE 'LogXMLResponse'
    service: GLDMessageLog:LogXMLResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'createSoapData'
  service: pub.soap.utils:createSoapData
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'addBodyEntry'
  service: pub.soap.utils:addBodyEntry
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

## Package: GLDFundingEngine

### `GLDFundingEngine/MainFlows/processACHBatch`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'getSystemDateTime' [DISABLED]
      service: GLDACHAdapterServices:getSystemDateTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getSystemDateTime'
      service: GLDExpressAdapterServices.Funding:getSystemDateTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'selectACHBatch' [DISABLED]
      service: GLDACHAdapterServices:selectACHBatch
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'selectACHBatch'
      service: GLDExpressAdapterServices.Funding:selectACHBatch
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getNextBatchID' [DISABLED]
      service: GLDACHAdapterServices:getNextBatchID
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getNextBatchID'
      service: GLDExpressAdapterServices.Funding:getNextBatchID
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'formatRoutingNumber'
      service: GLDFundingEngine.ProcessFlows:formatRoutingNumber
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'formatRoutingNumber'
      service: GLDFundingEngine.ProcessFlows:formatRoutingNumber
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    INVOKE 'getCurrentDate'
      service: pub.date:getCurrentDate
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'formatDate'
      service: pub.date:formatDate
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'formatDate'
      service: pub.date:formatDate
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'addDateTime'
      service: GLDExpressGateway.Utilities.JavaServices:addDateTime
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    LOOP over '?'
      INVOKE 'padLeft'
        service: pub.string:padLeft
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'concat'
        service: pub.string:concat
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      INVOKE 'padLeft'
        service: pub.string:padLeft
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
      MAP [mode=STANDALONE]
      END-MAP
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-LOOP
    INVOKE 'padLeft'
      service: pub.string:padLeft
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'length'
      service: pub.string:length
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on '/hashLength'
      SEQUENCE '&lt;10' exit-on=FAILURE
        INVOKE 'padLeft'
          service: pub.string:padLeft
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '&gt;10' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
      SEQUENCE '10' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    INVOKE 'padLeft'
      service: pub.string:padLeft
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'padLeft'
      service: pub.string:padLeft
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
      MAP [mode=INVOKEINPUT]
      END-MAP
      MAP [mode=INVOKEOUTPUT]
      END-MAP
    END-MAP
    INVOKE 'divideInts'
      service: pub.math:divideInts
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    BRANCH on ''
      SEQUENCE '%quotient% &lt; 1' exit-on=FAILURE
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
      SEQUENCE '%quotient% &gt; 0' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-SEQUENCE
    END-BRANCH
    BRANCH on ''
      SEQUENCE '%count% &gt; 0' exit-on=FAILURE
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
        END-MAP
        RETRY max=%count%
          MAP [mode=STANDALONE]
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
        END-RETRY
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
        MAP [mode=STANDALONE]
        END-MAP
      END-SEQUENCE
    END-BRANCH
    INVOKE 'padLeft'
      service: pub.string:padLeft
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'convertToString'
      service: pub.flatFile:convertToString
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'updateBatchIDs' [DISABLED]
      service: GLDACHAdapterServices:updateBatchIDs
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'updateBatchIDs'
      service: GLDExpressAdapterServices.Funding:updateBatchIDs
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'ftp' [DISABLED]
        service: pub.client:ftp
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      INVOKE 'sendEmail'
        service: WSRCommon.Utilities.FlowServices:sendEmail
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    SEQUENCE '' exit-on=DONE
      INVOKE 'LogXMLRequest'
        service: GLDMessageLog:LogXMLRequest
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
    END-SEQUENCE
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDFundingEngine/MainFlows/processFundingRequest`

```
BRANCH on '/debug'
  INVOKE '$null'
    service: pub.flow:savePipelineToFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  INVOKE 'true'
    service: pub.flow:restorePipelineFromFile
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-BRANCH
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    MAP [mode=STANDALONE]
    END-MAP
    LOOP over '?'
      SEQUENCE '' exit-on=SUCCESS
        SEQUENCE '' exit-on=FAILURE
          BRANCH on '/fundingEngineWrapperInput/ns1:fundingEngineWrapper/fundingRequest/payments/payment/type'
            SEQUENCE 'Check' exit-on=FAILURE
              INVOKE 'invokeGetUniquePayee'
                service: GLDExpressGateway.ProcessFlows.CheckWriter:invokeGetUniquePayee
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
              BRANCH on '/payeeKey'
                INVOKE '$null'
                  service: GLDExpressGateway.ProcessFlows.CheckWriter:invokeAddNewPayee
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
              END-BRANCH
              INVOKE 'invokeCreateCheckRequest'
                service: GLDExpressGateway.ProcessFlows.CheckWriter:invokeCreateCheckRequest
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
              MAP [mode=STANDALONE]
              END-MAP
            END-SEQUENCE
            SEQUENCE 'ACH' exit-on=FAILURE
              INVOKE 'insertPayment' [DISABLED]
                service: GLDACHAdapterServices:insertPayment
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
              INVOKE 'insertPayment'
                service: GLDExpressAdapterServices.Funding:insertPayment
                MAP [mode=INPUT]
                END-MAP
                MAP [mode=OUTPUT]
                END-MAP
              END-INVOKE
              MAP [mode=STANDALONE]
              END-MAP
            END-SEQUENCE
            SEQUENCE '$default' exit-on=FAILURE
              MAP [mode=STANDALONE]
              END-MAP
            END-SEQUENCE
          END-BRANCH
        END-SEQUENCE
        SEQUENCE '' exit-on=DONE
          INVOKE 'getLastError'
            service: pub.flow:getLastError
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          MAP [mode=STANDALONE]
          END-MAP
          MAP [mode=STANDALONE]
          END-MAP
          MAP [mode=STANDALONE]
            MAP [mode=INVOKEINPUT]
            END-MAP
            MAP [mode=INVOKEOUTPUT]
            END-MAP
          END-MAP
          INVOKE 'publishErrorDoc'
            service: WSRProcessStatistics.MainFlows:publishErrorDoc
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-SEQUENCE
    END-LOOP
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
    END-LOOP
    MAP [mode=STANDALONE]
    END-MAP
    MAP [mode=STANDALONE]
    END-MAP
    INVOKE 'publishErrorDoc'
      service: WSRProcessStatistics.MainFlows:publishErrorDoc
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
END-SEQUENCE
```

### `GLDFundingEngine/ProcessFlows/formatRoutingNumber`

```
INVOKE 'trim'
  service: pub.string:trim
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'padLeft'
  service: pub.string:padLeft
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDFundingEngine/Wrappers/Registration/registerFlowServiceForSOAP`

```
INVOKE 'registerProcessor'
  service: pub.soap.processor:registerProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDFundingEngine/Wrappers/Registration/unregisterFlowServiceForSOAP`

```
INVOKE 'unregisterProcessor'
  service: pub.soap.processor:unregisterProcessor
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

### `GLDFundingEngine/Wrappers/fundingEngineWrapper`

```
INVOKE 'getBody'
  service: pub.soap.utils:getBody
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlNodeToDocument'
  service: pub.xml:xmlNodeToDocument
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
MAP [mode=STANDALONE]
END-MAP
SEQUENCE '' exit-on=FAILURE
  INVOKE 'LogXMLRequest'
    service: GLDMessageLog:LogXMLRequest
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'processFundingRequest'
      service: GLDFundingEngine.MainFlows:processFundingRequest
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    LOOP over '?'
      MAP [mode=STANDALONE]
      END-MAP
    END-LOOP
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
END-SEQUENCE
SEQUENCE '' exit-on=FAILURE
  INVOKE 'LogXMLResponse'
    service: GLDMessageLog:LogXMLResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
INVOKE 'documentToXMLString'
  service: pub.xml:documentToXMLString
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'xmlStringToXMLNode'
  service: pub.xml:xmlStringToXMLNode
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'createSoapData'
  service: pub.soap.utils:createSoapData
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'addBodyEntry'
  service: pub.soap.utils:addBodyEntry
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
```

## Package: GLDMessageLog

### `GLDMessageLog/LogRequestAndResponse`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    SEQUENCE '' exit-on=FAILURE
      BRANCH on '/clientApplication'
        SEQUENCE 'GLD' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
        SEQUENCE 'EFW' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
        SEQUENCE 'VMR' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
        SEQUENCE 'gldExpressGateway' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
        END-SEQUENCE
      END-BRANCH
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      BRANCH on '/request/requestDoc'
        MAP [mode=STANDALONE]
        END-MAP
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
      BRANCH on '/request/request'
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-BRANCH
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      BRANCH on '/response/responseDoc'
        MAP [mode=STANDALONE]
        END-MAP
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
      BRANCH on '/response/response'
        MAP [mode=STANDALONE]
        END-MAP
        MAP [mode=STANDALONE]
          MAP [mode=INVOKEINPUT]
          END-MAP
          MAP [mode=INVOKEOUTPUT]
          END-MAP
        END-MAP
      END-BRANCH
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'GetNextMessageLogID'
        service: GLDMessageLogAdapterServices:GetNextMessageLogID
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
    INVOKE 'getCurrentDate'
      service: pub.date:getCurrentDate
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'LogRequestAndResponse'
      service: WBMTesting.RyanTesting.Util:LogRequestAndResponse
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    MAP [mode=STANDALONE]
    END-MAP
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
END-SEQUENCE
END-SEQUENCE
```

### `GLDMessageLog/LogXMLRequest`

```
SEQUENCE '' exit-on=DONE
  INVOKE 'GetNextMessageLogID'
    service: GLDMessageLogAdapterServices:GetNextMessageLogID
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '/RequestDoc'
    SEQUENCE '$null' exit-on=FAILURE
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      BRANCH on '/documentTypeName'
        SEQUENCE '$null' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-BRANCH
  BRANCH on ''
    SEQUENCE '%Request% ==$null || %Request% == ''' exit-on=FAILURE
      MAP [mode=STANDALONE]
      END-MAP
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      MAP [mode=STANDALONE]
        MAP [mode=INVOKEINPUT]
        END-MAP
        MAP [mode=INVOKEOUTPUT]
        END-MAP
      END-MAP
    END-SEQUENCE
  END-BRANCH
  INVOKE 'LogXMLRequest'
    service: GLDMessageLogAdapterServices:LogXMLRequest
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE]
  END-MAP
END-SEQUENCE
```

### `GLDMessageLog/LogXMLResponse`

```
INVOKE 'savePipelineToFile' [DISABLED]
  service: pub.flow:savePipelineToFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
INVOKE 'restorePipelineFromFile' [DISABLED]
  service: pub.flow:restorePipelineFromFile
  MAP [mode=INPUT]
  END-MAP
  MAP [mode=OUTPUT]
  END-MAP
END-INVOKE
SEQUENCE '' exit-on=DONE
  INVOKE 'GetOracleSysDate' [DISABLED]
    service: GLDMessageLogAdapterServices:GetOracleSysDate
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
  MAP [mode=STANDALONE] [DISABLED]
  END-MAP
  MAP [mode=STANDALONE] [DISABLED]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  BRANCH on '/ResponseDoc'
    SEQUENCE '$null' exit-on=FAILURE
    END-SEQUENCE
    SEQUENCE '$default' exit-on=FAILURE
      BRANCH on '/documentTypeName'
        SEQUENCE '$null' exit-on=FAILURE
          MAP [mode=STANDALONE]
          END-MAP
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
        SEQUENCE '$default' exit-on=FAILURE
          INVOKE 'documentToXMLString'
            service: pub.xml:documentToXMLString
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
  END-BRANCH
  MAP [mode=STANDALONE]
    MAP [mode=INVOKEINPUT]
    END-MAP
    MAP [mode=INVOKEOUTPUT]
    END-MAP
  END-MAP
  INVOKE 'LogXMLResponse'
    service: GLDMessageLogAdapterServices:LogXMLResponse
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
MAP [mode=STANDALONE]
END-MAP
```

## Package: GLDSoap

### `GLDSoap/ProcessFlows/invokeSOAPService`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'createSoapData'
      service: pub.soap.utils:createSoapData
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getNodeName'
      service: GLDSoap.Utilities.JavaServices:getNodeName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'isNullOrBlank'
        service: GLDExpressGateway.Utilities.FlowServices:isNullOrBlank
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on ''
        SEQUENCE 'result='false'' exit-on=FAILURE
          INVOKE 'stringToSoapData'
            service: pub.soap.utils:stringToSoapData
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
        SEQUENCE 'result='true'' exit-on=FAILURE
          SEQUENCE '' exit-on=FAILURE
            BRANCH on '/prefix'
              SEQUENCE '$null' exit-on=FAILURE
                INVOKE 'addNameSpace'
                  service: GLDSoap.Utilities.JavaServices:addNameSpace
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
              END-SEQUENCE
              SEQUENCE '$default' exit-on=FAILURE
                INVOKE 'addNameSpace'
                  service: GLDSoap.Utilities.JavaServices:addNameSpace
                  MAP [mode=INPUT]
                  END-MAP
                  MAP [mode=OUTPUT]
                  END-MAP
                END-INVOKE
              END-SEQUENCE
            END-BRANCH
            INVOKE 'documentToXMLString'
              service: pub.xml:documentToXMLString
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE 'xmlStringToXMLNode'
              service: pub.xml:xmlStringToXMLNode
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
          SEQUENCE '' exit-on=FAILURE
            INVOKE 'addBodyEntry'
              service: pub.soap.utils:addBodyEntry
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'soapHTTP'
        service: pub.client:soapHTTP
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/soapStatus'
        SEQUENCE '0' exit-on=FAILURE
          INVOKE 'getBody'
            service: pub.soap.utils:getBody
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on '/responseDocumentTypeName'
            SEQUENCE '$null' exit-on=FAILURE
              BRANCH on '/nameSpace'
                SEQUENCE '$null' exit-on=FAILURE
                  INVOKE 'xmlNodeToDocument'
                    service: pub.xml:xmlNodeToDocument
                    MAP [mode=INPUT]
                    END-MAP
                    MAP [mode=OUTPUT]
                    END-MAP
                  END-INVOKE
                END-SEQUENCE
                SEQUENCE '$default' exit-on=FAILURE
                  INVOKE 'xmlNodeToDocument'
                    service: pub.xml:xmlNodeToDocument
                    MAP [mode=INPUT]
                    END-MAP
                    MAP [mode=OUTPUT]
                    END-MAP
                  END-INVOKE
                END-SEQUENCE
              END-BRANCH
            END-SEQUENCE
            SEQUENCE '$default' exit-on=FAILURE
              BRANCH on '/nameSpace'
                SEQUENCE '$null' exit-on=FAILURE
                  INVOKE 'xmlNodeToDocument'
                    service: pub.xml:xmlNodeToDocument
                    MAP [mode=INPUT]
                    END-MAP
                    MAP [mode=OUTPUT]
                    END-MAP
                  END-INVOKE
                END-SEQUENCE
                SEQUENCE '$default' exit-on=FAILURE
                  INVOKE 'xmlNodeToDocument'
                    service: pub.xml:xmlNodeToDocument
                    MAP [mode=INPUT]
                    END-MAP
                    MAP [mode=OUTPUT]
                    END-MAP
                  END-INVOKE
                END-SEQUENCE
              END-BRANCH
            END-SEQUENCE
          END-BRANCH
          BRANCH on '/validateInputEnabled'
            INVOKE 'true'
              service: pub.schema:validate
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-BRANCH
        END-SEQUENCE
        SEQUENCE '1' exit-on=FAILURE
          INVOKE 'getBodyEntries'
            service: pub.soap.utils:getBodyEntries
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlNodeToDocument'
            service: pub.xml:xmlNodeToDocument
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
      END-SEQUENCE
    END-BRANCH
  END-SEQUENCE
  INVOKE 'clearPipeline'
    service: pub.flow:clearPipeline
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
SEQUENCE '' exit-on=DONE
  INVOKE 'getLastError'
    service: pub.flow:getLastError
    MAP [mode=INPUT]
    END-MAP
    MAP [mode=OUTPUT]
    END-MAP
  END-INVOKE
END-SEQUENCE
END-SEQUENCE
```

### `GLDSoap/ProcessFlows/invokeSOAPService_1`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'createSoapData'
      service: pub.soap.utils:createSoapData
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getNodeName'
      service: GLDSoap.Utilities.JavaServices:getNodeName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      SEQUENCE '' exit-on=FAILURE
        BRANCH on '/prefix'
          SEQUENCE '$null' exit-on=FAILURE
            INVOKE 'addNameSpace'
              service: GLDSoap.Utilities.JavaServices:addNameSpace
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            INVOKE 'addNameSpace'
              service: GLDSoap.Utilities.JavaServices:addNameSpace
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
        INVOKE 'documentToXMLString'
          service: pub.xml:documentToXMLString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'xmlStringToXMLNode'
          service: pub.xml:xmlStringToXMLNode
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'addBodyEntry'
          service: pub.soap.utils:addBodyEntry
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'soapDataToString'
          service: pub.soap.utils:soapDataToString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        BRANCH on ''
          SEQUENCE 'ForceSoapData!=null' exit-on=FAILURE
            INVOKE 'stringToSoapData'
              service: pub.soap.utils:stringToSoapData
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
      END-SEQUENCE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'soapHTTP'
        service: pub.client:soapHTTP
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/soapStatus'
        SEQUENCE '0' exit-on=FAILURE
          INVOKE 'getBody'
            service: pub.soap.utils:getBody
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on '/responseDocumentTypeName'
            INVOKE '$null'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE '$default'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-BRANCH
          BRANCH on '/validateInputEnabled'
            INVOKE 'true'
              service: pub.schema:validate
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-BRANCH
        END-SEQUENCE
        SEQUENCE '1' exit-on=FAILURE
          INVOKE 'getBodyEntries'
            service: pub.soap.utils:getBodyEntries
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlNodeToDocument'
            service: pub.xml:xmlNodeToDocument
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
    INVOKE 'clearPipeline'
      service: pub.flow:clearPipeline
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
END-SEQUENCE
END-SEQUENCE
```

### `GLDSoap/ProcessFlows/invokeSOAPService_BeforeXmlHeader`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'createSoapData'
      service: pub.soap.utils:createSoapData
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getNodeName'
      service: GLDSoap.Utilities.JavaServices:getNodeName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      SEQUENCE '' exit-on=FAILURE
        BRANCH on '/prefix'
          SEQUENCE '$null' exit-on=FAILURE
            INVOKE 'addNameSpace'
              service: GLDSoap.Utilities.JavaServices:addNameSpace
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            INVOKE 'addNameSpace'
              service: GLDSoap.Utilities.JavaServices:addNameSpace
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
        INVOKE 'documentToXMLString'
          service: pub.xml:documentToXMLString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'xmlStringToXMLNode'
          service: pub.xml:xmlStringToXMLNode
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'addBodyEntry'
          service: pub.soap.utils:addBodyEntry
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'soapDataToString'
          service: pub.soap.utils:soapDataToString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'soapHTTP'
        service: pub.client:soapHTTP
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/soapStatus'
        SEQUENCE '0' exit-on=FAILURE
          INVOKE 'getBody'
            service: pub.soap.utils:getBody
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on '/responseDocumentTypeName'
            INVOKE '$null'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE '$default'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-BRANCH
          BRANCH on '/validateInputEnabled'
            INVOKE 'true'
              service: pub.schema:validate
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-BRANCH
        END-SEQUENCE
        SEQUENCE '1' exit-on=FAILURE
          INVOKE 'getBodyEntries'
            service: pub.soap.utils:getBodyEntries
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlNodeToDocument'
            service: pub.xml:xmlNodeToDocument
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
    INVOKE 'clearPipeline'
      service: pub.flow:clearPipeline
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
END-SEQUENCE
END-SEQUENCE
```

## Package: GLDSoap20

### `GLDSoap20/ProcessFlows/invokeSOAPService`

```
SEQUENCE '' exit-on=SUCCESS
  SEQUENCE '' exit-on=FAILURE
    INVOKE 'createSoapData'
      service: pub.soap.utils:createSoapData
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    INVOKE 'getNodeName'
      service: GLDSoap.Utilities.JavaServices:getNodeName
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
    SEQUENCE '' exit-on=FAILURE
      SEQUENCE '' exit-on=FAILURE
        BRANCH on '/prefix'
          SEQUENCE '$null' exit-on=FAILURE
            INVOKE 'addNameSpace'
              service: GLDSoap.Utilities.JavaServices:addNameSpace
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
          SEQUENCE '$default' exit-on=FAILURE
            INVOKE 'addNameSpace'
              service: GLDSoap.Utilities.JavaServices:addNameSpace
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-SEQUENCE
        END-BRANCH
        INVOKE 'documentToXMLString'
          service: pub.xml:documentToXMLString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'xmlStringToXMLNode'
          service: pub.xml:xmlStringToXMLNode
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
      SEQUENCE '' exit-on=FAILURE
        INVOKE 'addBodyEntry'
          service: pub.soap.utils:addBodyEntry
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
        INVOKE 'soapDataToString'
          service: pub.soap.utils:soapDataToString
          MAP [mode=INPUT]
          END-MAP
          MAP [mode=OUTPUT]
          END-MAP
        END-INVOKE
      END-SEQUENCE
    END-SEQUENCE
    SEQUENCE '' exit-on=FAILURE
      INVOKE 'soapHTTP'
        service: pub.client:soapHTTP
        MAP [mode=INPUT]
        END-MAP
        MAP [mode=OUTPUT]
        END-MAP
      END-INVOKE
      BRANCH on '/soapStatus'
        SEQUENCE '0' exit-on=FAILURE
          INVOKE 'getBody'
            service: pub.soap.utils:getBody
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          BRANCH on '/responseDocumentTypeName'
            INVOKE '$null'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
            INVOKE '$default'
              service: pub.xml:xmlNodeToDocument
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-BRANCH
          BRANCH on '/validateInputEnabled'
            INVOKE 'true'
              service: pub.schema:validate
              MAP [mode=INPUT]
              END-MAP
              MAP [mode=OUTPUT]
              END-MAP
            END-INVOKE
          END-BRANCH
        END-SEQUENCE
        SEQUENCE '1' exit-on=FAILURE
          INVOKE 'getBodyEntries'
            service: pub.soap.utils:getBodyEntries
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
          INVOKE 'xmlNodeToDocument'
            service: pub.xml:xmlNodeToDocument
            MAP [mode=INPUT]
            END-MAP
            MAP [mode=OUTPUT]
            END-MAP
          END-INVOKE
        END-SEQUENCE
      END-BRANCH
    END-SEQUENCE
    INVOKE 'clearPipeline'
      service: pub.flow:clearPipeline
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
  END-SEQUENCE
  SEQUENCE '' exit-on=DONE
    INVOKE 'getLastError'
      service: pub.flow:getLastError
      MAP [mode=INPUT]
      END-MAP
      MAP [mode=OUTPUT]
      END-MAP
    END-INVOKE
END-SEQUENCE
END-SEQUENCE
```

---

## Java Custom Services — Full Source

### `GLDComplianceCheck.Utilities`

```java
package GLDComplianceCheck.Utilities;

// -----( IS Java Code Template v1.2
// -----( CREATED: 2007-10-26 13:32:05 EDT
// -----( ON-HOST: cwb02dwmis02.keybank.com

import com.wm.data.*;
import com.wm.util.Values;
import com.wm.app.b2b.server.Service;
import com.wm.app.b2b.server.ServiceException;
// --- <<IS-START-IMPORTS>> ---
// --- <<IS-END-IMPORTS>> ---

public final class JavaServices

{
	// ---( internal utility methods )---

	final static JavaServices _instance = new JavaServices();

	static JavaServices _newInstance() { return new JavaServices(); }

	static JavaServices _cast(Object o) { return (JavaServices)o; }

	// ---( server methods )---




	public static final void isNullOrBlank (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(isNullOrBlank)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required inString
		// [o] field:0:required result
		IDataCursor idc = pipeline.getCursor( );
		String inStr ="";
		
		if(idc.first("inString"))
		{
		inStr = (String)idc.getValue();
		}
		
		if( inStr == null )
		{
		                 idc.last();
				 idc.insertAfter("result", "true" );
				 
		}
		
		inStr = inStr.trim();
		
		if( inStr.equals("") )
		{
		                 idc.last();
				 idc.insertAfter("result", "true" );
				 
		}
		else if (inStr.length()>0)
		{
		                 idc.last();
				 idc.insertAfter("result", "false" );
		}
		inStr="";
		idc.destroy();
		
		// --- <<IS-END>> ---

                
	}



	public static final void isNumericOrEmpty (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(isNumericOrEmpty)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required inNum
		// [o] field:0:required isNumeric
		IDataCursor idc = pipeline.getCursor( );
		String inNum ="";
		
		if(idc.first("inNum"))
		{
		inNum = (String)idc.getValue();
		}
		
		try{
		if(inNum==""){
		
		idc.insertAfter("isNumeric", "true" );
		}
		else {
		
		Long num = new Long(inNum);
		 idc.insertAfter("isNumeric", "true" );
		}
		}
		
		catch(NumberFormatException nfex)
				{
					idc.last();
				 idc.insertAfter("isNumeric", "false" );
				}
		
		
		inNum="";
		idc.destroy();
		
		// --- <<IS-END>> ---

                
	}



	public static final void isPositiveNumber (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(isPositiveNumber)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required inNum
		// [o] field:0:required isPositive
		IDataCursor idc = pipeline.getCursor( );
		String inNum ="";
		
		if(idc.first("inNum"))
		{
		inNum = (String)idc.getValue();
		}
		
		try{
			if(inNum!=null){
		
			Long num = new Long(inNum);
		
			if(num.longValue() >0)
		             {
			 idc.insertAfter("isPositive", "true" );
		             }
			else{
		 idc.insertAfter("isPositive", "false" );
		            }
			}
		}
		
		catch(NumberFormatException nfex)
				{
					idc.last();
				 idc.insertAfter("isPositive", "false" );
				}
		
		
		inNum="";
		idc.destroy();
		
		// --- <<IS-END>> ---

                
	}
}


```

### `GLDExpressGateway.ProcessFlows.Applicant`

```java
package GLDExpressGateway.ProcessFlows.Applicant;

// -----( IS Java Code Template v1.2
// -----( CREATED: 2008-09-25 21:19:10 EDT
// -----( ON-HOST: csc06dwmis01.keybank.com

import com.wm.data.*;
import com.wm.util.Values;
import com.wm.app.b2b.server.Service;
import com.wm.app.b2b.server.ServiceException;
// --- <<IS-START-IMPORTS>> ---
import com.keybank.kef.bop.*;
import com.keybank.kef.bop.model.*;
// --- <<IS-END-IMPORTS>> ---

public final class JavaServices

{
	// ---( internal utility methods )---

	final static JavaServices _instance = new JavaServices();

	static JavaServices _newInstance() { return new JavaServices(); }

	static JavaServices _cast(Object o) { return (JavaServices)o; }

	// ---( server methods )---




	public static final void invokeXOS_EFWApplicantMatch (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(invokeXOS_EFWApplicantMatch)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [o] field:0:required Reason
		// [o] field:0:required MatchCode
			//matching variables
			ExpressFinancingCustomerData efwData = null;
			ExpressLinkCustomerData xlData = null;
		
			// pipeline
			IDataCursor pipelineCursor = pipeline.getCursor();
		
			// EFWCustomer 
			IData	EFWCustomer = IDataUtil.getIData( pipelineCursor, "EFWCustomer" );
			if ( EFWCustomer != null)
			{
				IDataCursor EFWCustomerCursor = EFWCustomer.getCursor(); 
		
					String	efwCompanyName = IDataUtil.getString( EFWCustomerCursor, "CompanyName" );
					String	efwDBAName = IDataUtil.getString( EFWCustomerCursor, "DBAName" );
					String	efwFederalTaxId = IDataUtil.getString( EFWCustomerCursor, "FederalTaxId" );
					String	efwDunsNumber = IDataUtil.getString( EFWCustomerCursor, "DunsNumber" );
					String	efwPhone = null;
					String	efwStreetAddress = null;
					String	efwZip = null;
		
					// i.Address
					IData	Address = IDataUtil.getIData( EFWCustomerCursor, "Address" );
					if ( Address != null)
					{
						IDataCursor AddressCursor = Address.getCursor();
							efwPhone = IDataUtil.getString( AddressCursor, "Phone" );
							efwStreetAddress = IDataUtil.getString( AddressCursor, "StreetAddress" );
							efwZip = IDataUtil.getString( AddressCursor, "Zip" );
						AddressCursor.destroy();
					}
		
					efwData = new ExpressFinancingCustomerData(efwDunsNumber, efwFederalTaxId, efwDBAName, efwCompanyName, efwStreetAddress, efwZip, efwPhone);
				EFWCustomerCursor.destroy();
			}
		
			// EFWPGs
			IData	EFWPGs = IDataUtil.getIData( pipelineCursor, "EFWPGs" );
			if ( EFWPGs != null)
			{
				IDataCursor EFWPGsCursor = EFWPGs.getCursor();
		
					// i.Contact
					IData[]	Contact = IDataUtil.getIDataArray( EFWPGsCursor, "Contact" );
					if ( Contact != null)
					{
						for ( int i = 0; i < Contact.length; i++ )
						{
							IDataCursor ContactCursor = Contact[i].getCursor();
								String	FirstName = IDataUtil.getString( ContactCursor, "FirstName" );
								String	LastName = IDataUtil.getString( ContactCursor, "LastName" );
								String	Phone_1 = IDataUtil.getString( ContactCursor, "Phone" );
								String	SSN = IDataUtil.getString( ContactCursor, "SSN" );
								String	StreetAddress_1 = IDataUtil.getString( ContactCursor, "StreetAddress" );
								String	Zip_1 = IDataUtil.getString( ContactCursor, "Zip" );
							ContactCursor.destroy();
							efwData.addPG(SSN, FirstName, LastName, StreetAddress_1, Zip_1, Phone_1);
						}
					}
				EFWPGsCursor.destroy();
			}
		
		
			// XOSApplicant
			IData	XOSApplicant = IDataUtil.getIData( pipelineCursor, "XOSApplicant" );
			if ( XOSApplicant != null)
			{
				IDataCursor XOSApplicantCursor = XOSApplicant.getCursor();
		
					// i.companyInfo
					IData	companyInfo = IDataUtil.getIData( XOSApplicantCursor, "companyInfo" );
					if ( companyInfo != null)
					{
						IDataCursor companyInfoCursor = companyInfo.getCursor();
							String	dunsNumber = IDataUtil.getString( companyInfoCursor, "dunsNumber" );
							String[]	lesseeDUNSNumbers = IDataUtil.getStringArray( companyInfoCursor, "lesseeDUNSNumbers" );
							String	taxNumber = IDataUtil.getString( companyInfoCursor, "taxNumber" );
							String	businessName = IDataUtil.getString( companyInfoCursor, "businessName" );
							String[]	otherBusinessName = IDataUtil.getStringArray( companyInfoCursor, "otherBusinessName" );
							String	legalName = IDataUtil.getString( companyInfoCursor, "legalName" );
							String	addressLine1 = IDataUtil.getString( companyInfoCursor, "addressLine1" );
							String	postalCode = IDataUtil.getString( companyInfoCursor, "postalCode" );
							String	phoneNumber = IDataUtil.getString( companyInfoCursor, "phoneNumber" );
							String[]	billingContactPhone = IDataUtil.getStringArray( companyInfoCursor, "billingContactPhone" );
							String	statusDescription = IDataUtil.getString( companyInfoCursor, "statusDescription" );				
						companyInfoCursor.destroy();
						boolean active = true;
						if((statusDescription != null) && (statusDescription == "inactive")){
							active = false;
						}
						xlData = new ExpressLinkCustomerData(dunsNumber, taxNumber, businessName, legalName, addressLine1, postalCode, phoneNumber, active);
						if(lesseeDUNSNumbers != null){
							for ( int i = 0; i < lesseeDUNSNumbers.length; i++ )
							{
								xlData.addLesseeDunsNumber(lesseeDUNSNumbers[i]);
							}
						}
						if(otherBusinessName != null){
						{
							for ( int i = 0; i < otherBusinessName.length; i++ )
							{
								xlData.addDbaName(otherBusinessName[i]);
							}
						}
						if(billingContactPhone != null)
							for ( int i = 0; i < billingContactPhone.length; i++ )
							{
								xlData.addBillingContactPhone(billingContactPhone[i]);
							}
						}
					}
		
					// i.BillingInfo
					IData[]	BillingInfo = IDataUtil.getIDataArray( XOSApplicantCursor, "BillingInfo" );
					if ( BillingInfo != null)
					{
						for ( int i = 0; i < BillingInfo.length; i++ )
						{
							IDataCursor BillingInfoCursor = BillingInfo[i].getCursor();
								String	Name = IDataUtil.getString( BillingInfoCursor, "Name" );
								String	Address1 = IDataUtil.getString( BillingInfoCursor, "Address1" );
								String	Zip = IDataUtil.getString( BillingInfoCursor, "Zip" );
								String	Status = IDataUtil.getString( BillingInfoCursor, "Status" );
							BillingInfoCursor.destroy();
							boolean active = true;
							if((Status != null) && ((Status == "inactive")||(Status == "Disabled"))){
								active = false;
							}
							xlData.addBilling(Name, Address1, Zip, active);
						}
					}
		
					// i_1.relatedSignors
					IData[]	relatedSignors = IDataUtil.getIDataArray( XOSApplicantCursor, "relatedSignors" );
					if ( relatedSignors != null)
					{
						for ( int i_1 = 0; i_1 < relatedSignors.length; i_1++ )
						{
							IDataCursor relatedSignorsCursor = relatedSignors[i_1].getCursor();
								String	SSN = IDataUtil.getString( relatedSignorsCursor, "SSN" );
								String	firstName = IDataUtil.getString( relatedSignorsCursor, "firstName" );
								String	lastName = IDataUtil.getString( relatedSignorsCursor, "lastName" );
								String	addressLine1 = IDataUtil.getString( relatedSignorsCursor, "addressLine1" );
								String	phoneNumber = IDataUtil.getString( relatedSignorsCursor, "phoneNumber" );
								String  postalCode = IDataUtil.getString( relatedSignorsCursor, "postalCode" );
								String	statusDescription = IDataUtil.getString( relatedSignorsCursor, "statusDescription" );
							relatedSignorsCursor.destroy();
							xlData.addSignor(SSN, firstName, lastName, addressLine1, postalCode, phoneNumber);
						}
					}
				XOSApplicantCursor.destroy();
			}
		pipelineCursor.destroy();
		CustomerMatcher matcher = new CustomerMatcher();
		CustomerMatchResult result = matcher.match(efwData, xlData);
		String reason = result.getReason();
		String matchStatus = "No Match";
		if (result.isExactMatch()){
			matchStatus = "Exact";
		}
		else if (result.isSimilarMatch()){
			matchStatus = "Similar";
		}
		// pipeline
		IDataCursor pipelineCursor_1 = pipeline.getCursor();
		IDataUtil.put( pipelineCursor_1, "Reason", reason);
		IDataUtil.put( pipelineCursor_1, "MatchCode", matchStatus);
		pipelineCursor_1.destroy();
		// --- <<IS-END>> ---

                
	}
}


```

### `GLDExpressGateway.ProcessFlows.Customer`

```java
package GLDExpressGateway.ProcessFlows.Customer;

// -----( IS Java Code Template v1.2
// -----( CREATED: 2008-09-30 14:32:25 EDT
// -----( ON-HOST: csc06dwmis01.keybank.com

import com.wm.data.*;
import com.wm.util.Values;
import com.wm.app.b2b.server.Service;
import com.wm.app.b2b.server.ServiceException;
// --- <<IS-START-IMPORTS>> ---
import com.keybank.kef.lpk2xoscu.model.lpk.*;
import com.keybank.kef.lpk2xoscu.model.xos.*;
import com.keybank.kef.lpk2xoscu.*;
import java.util.*;
import java.text.*;
import com.keybank.kef.lpk2xoscu.util.*;
import com.keybank.kef.lpk2xoscu.core.*;
import com.keybank.kef.lpk2xoscu.wm.*;
import java.util.Calendar;
import java.io.*;
// --- <<IS-END-IMPORTS>> ---

public final class JavaServices

{
	// ---( internal utility methods )---

	final static JavaServices _instance = new JavaServices();

	static JavaServices _newInstance() { return new JavaServices(); }

	static JavaServices _cast(Object o) { return (JavaServices)o; }

	// ---( server methods )---




	public static final void Untitled (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(Untitled)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required initialLoad
		
		// pipeline
		IDataCursor pipelineCursor = pipeline.getCursor();
			String	initialLoad = IDataUtil.getString( pipelineCursor, "initialLoad" );
		pipelineCursor.destroy();
		// --- <<IS-END>> ---

                
	}



	public static final void determineXLinkCustomerUpdate (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(determineXLinkCustomerUpdate)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		
		// pipeline
		IDataCursor pipelineCursor = pipeline.getCursor();
		
			// inputLpkCustomerUpdateData
			IData	inputLpkCustomerUpdateData = IDataUtil.getIData( pipelineCursor, "inputLpkCustomerUpdateData" );
		 
			String	initialLoad = IDataUtil.getString( pipelineCursor, "initialLoad" );
			boolean initLoad = false;
			try { initLoad = new Boolean(initialLoad).booleanValue(); } catch (Exception e) {};
		
		
			IData	inputApplicant = IDataUtil.getIData( pipelineCursor, "inputApplicant" );
		
			if ((inputApplicant == null) && (inputLpkCustomerUpdateData == null))
		                     throw new ServiceException("You must provide at least an inputLpkCustomerUpdateData or inputApplicant or both.");
		
			IData	inputCustomFieldEntities = IDataUtil.getIData( pipelineCursor, "inputCustomFieldEntities" );
		
			
			//****************************************************************************************
			//********************* PROCESS THE INPUT APPLICANT **************************************
			//****************************************************************************************
			
		
			Applicant xosApplicant = WebmethodsMarshalling.unmarshallApplicantFromIData(inputApplicant);
			
			//****************************************************************************************
			//********************* PROCESS THE CUSTOM FIELDS ****************************************
			//****************************************************************************************
			CustomFieldEntity[] xosCustomFieldEntities =  WebmethodsMarshalling.unmarshallCustomFieldEntitiesFromIData(inputCustomFieldEntities);
				
			//****************************************************************************************
			//********************* Process the LeasePack Customer Data ******************************
			//****************************************************************************************
		
			LpkCustomerUpdateBean[] lpkCustomerUpdateBeans = WebmethodsMarshalling.unmarshallLpkCustomUpdateBeansFromIData(inputLpkCustomerUpdateData);
			
			//******************************************************************************************
			//******************************* FINISHED PROCESSING INPUT DATA ***************************
			//******************************************************************************************
			pipelineCursor.destroy();
		
			//*******************************************************************************************
			//******************************* PERFORM THE CUSTOMER UPDATE LOGIC *************************
			//*******************************************************************************************
			
			CustomerUpdateResults results = null;
		
			try {             
			     results = CustomerUpdateService.updateCustomer(lpkCustomerUpdateBeans, xosApplicant, xosCustomFieldEntities, initLoad);
			}  catch (Throwable t) {
				ServiceException ex = new ServiceException("Error attempting to update customer from LeasePack");
				ex.initCause(t);
				throw ex;
			}
			if (results == null) throw new ServiceException("The results from the updateCustomer are null.");
			
			Applicant outApplicant = results.getApplicant();
			if (outApplicant == null) throw new ServiceException("Could not fetch the applicant from results. They are null.");
		
			CustomFieldEntity[] outCustomFieldEntities = results.getCustomFieldEntities();
			if (outCustomFieldEntities == null) throw new ServiceException("Could not fetch the CustomFieldEntities from results. They are null.");
			
			//*******************************************************************************************
			//******************************** UPDATE THE OUTPUT OBJECTS ********************************
			//*******************************************************************************************
		
			 IDataCursor pipelineCursor_1 = pipeline.getCursor();
		 
			//*******************************************************************************************
			//**************************** Output the Applicant  ****************************************
			//*******************************************************************************************
			 
			IData outputApplicant = WebmethodsMarshalling.marshallTheApplicantToIData(outApplicant);
			
			//*******************************************************************************************
			//********************* Output the Custom Fields  *******************************************
			//*******************************************************************************************
			
		        IData outputCustomFieldEntities = WebmethodsMarshalling.marshallCustomFieldEntitiesToIData(outCustomFieldEntities);
			
		
		// outputApplicant
		IDataUtil.put( pipelineCursor_1, "outputApplicant", outputApplicant );
		IDataUtil.put( pipelineCursor_1, "outputCustomFieldEntities", outputCustomFieldEntities );
		pipelineCursor_1.destroy();
		// --- <<IS-END>> ---

                
	}



	public static final void groupLpkCustomerData (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(groupLpkCustomerData)>> ---
		// @subtype unknown
		// @sigtype java 3.5

		/** This routine groups all Lpk2XosLpkCustomerData data passed in by "c_customer_number".
                    It returns them in the Lpk2XosGroupedLpkCustomerData document.
                    How does it do this? 
                    Well it loops through all of the Lpk2XosLpkCustomerData records.
		    It uses the "c_customer_number" for each as the key to a map which stores a list of Lpk2XosLpkCustomerData IData object.
                    If the "group" list cannot be found then it creates one, adds the Lpk2XosLpkCustomerData IData object to it
                    and stuffs it in the "groups" map (using the c_customer_number as the key).
		    It also puts the customerNumbers in a list just so that they are added into the final document in
                    the order in which they are encountered.  This is not a big deal but kind of thoughtful.
		    
		    Once all the Lpk2XosLpkCustomerData records have been processed it then prepares the output document.
                    Which basically amounts to iterating through the list of customerNumber and building the corresponding
                    CustomerGroup document, which consits of the customer number, and a set of Lpk2XosLpkCustomerData records
                    associated with the customer number (which can be obtained by looking in the "group" list contained in the 
                    "groups" map.
                 **/

		Map  groups = new HashMap();
		List customerNumbers = new ArrayList(); // keep things in some order
		IDataCursor pipelineCursor = pipeline.getCursor();

			IData	inputCustomerData = IDataUtil.getIData( pipelineCursor, "inputCustomerData" );
			if ( inputCustomerData != null)
			{
				IDataCursor inputCustomerDataCursor = inputCustomerData.getCursor();

					IData	LpkCustomerData = IDataUtil.getIData( inputCustomerDataCursor, "LpkCustomerData" );
					if ( LpkCustomerData != null)
					{
						IDataCursor LpkCustomerDataCursor = LpkCustomerData.getCursor();

							IData[]	LpkUpdateCustomerRecord = IDataUtil.getIDataArray( LpkCustomerDataCursor, "LpkUpdateCustomerRecord" );
							if ( LpkUpdateCustomerRecord != null)
							{
								for ( int i = 0; i < LpkUpdateCustomerRecord.length; i++ )
								{
									IDataCursor LpkUpdateCustomerRecordCursor = LpkUpdateCustomerRecord[i].getCursor();
										String	c_customer_number = IDataUtil.getString( LpkUpdateCustomerRecordCursor, "c_customer_number" );
										if ( c_customer_number == null) continue;
										c_customer_number = c_customer_number.trim();
										if ("0".equals(c_customer_number)) continue;										
										List group = (List) groups.get(c_customer_number);
										if (group == null) {
											group = new ArrayList();
											groups.put(c_customer_number, group);
											customerNumbers.add(c_customer_number);
										}
										group.add(LpkUpdateCustomerRecord[i]);
										
									LpkUpdateCustomerRecordCursor.destroy();
								}
							}
						LpkCustomerDataCursor.destroy();
					}
				inputCustomerDataCursor.destroy();
			}
		pipelineCursor.destroy();

		IDataCursor pipelineCursor_1 = pipeline.getCursor();

		IData	outputGroupedCustomerData = IDataFactory.create();
		IDataCursor outputGroupedCustomerDataCursor = outputGroupedCustomerData.getCursor();

		IData	customerGroups = IDataFactory.create();
		IDataCursor customerGroupsCursor = customerGroups.getCursor();

		IData[]	customerGroup = new IData[customerNumbers.size()];
		for (int idx = 0; idx < customerNumbers.size();idx++) 
		{
		    String customerNumber = (String) customerNumbers.get(idx);
			customerGroup[idx] = IDataFactory.create();
			IDataCursor customerGroupCursor = customerGroup[idx].getCursor();
			IDataUtil.put( customerGroupCursor, "c_customer_number",customerNumber);
	
			IData	customerData = IDataFactory.create();
			IDataCursor customerDataCursor = customerData.getCursor();
	
			IData	LpkCustomerData_1 = IDataFactory.create();
			IDataCursor LpkCustomerData_1Cursor = LpkCustomerData_1.getCursor();
			
			List group = (List) groups.get(customerNumber);
			if (group != null) 
				{
				IData[]	LpkUpdateCustomerRecord_1 = new IData[group.size()];
				for (int i=0;i<group.size();i++) {
					LpkUpdateCustomerRecord_1[i] = (IData) group.get(i);
				}
				IDataUtil.put( LpkCustomerData_1Cursor, "LpkUpdateCustomerRecord", LpkUpdateCustomerRecord_1 );
			    }
			LpkCustomerData_1Cursor.destroy();
			IDataUtil.put( customerDataCursor, "LpkCustomerData", LpkCustomerData_1 );
			customerDataCursor.destroy();
			IDataUtil.put( customerGroupCursor, "customerData", customerData );
			customerGroupCursor.destroy();
		}
		
		IDataUtil.put( customerGroupsCursor, "customerGroup", customerGroup );
		customerGroupsCursor.destroy();
		IDataUtil.put( outputGroupedCustomerDataCursor, "customerGroups", customerGroups );
		outputGroupedCustomerDataCursor.destroy();
		IDataUtil.put( pipelineCursor_1, "outputGroupedCustomerData", outputGroupedCustomerData );
		pipelineCursor_1.destroy();
		// --- <<IS-END>> ---

                
	}



	public static final void versionCheck (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(versionCheck)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required initialLoad
		// [o] field:0:required version
		
		IDataCursor pipelineCursor = pipeline.getCursor();
		IDataUtil.put( pipelineCursor, "version", Version.getVersion());
		pipelineCursor.destroy();
		// --- <<IS-END>> ---

                
	}

	// --- <<IS-START-SHARED>> ---
	
	
	// --- <<IS-END-SHARED>> ---
}


```

### `GLDExpressGateway.Utilities`

```java
package GLDExpressGateway.Utilities;

// -----( IS Java Code Template v1.2
// -----( CREATED: 2008-10-02 12:58:38 EDT
// -----( ON-HOST: csc06dwmis01.keybank.com

import com.wm.data.*;
import com.wm.util.Values;
import com.wm.app.b2b.server.Service;
import com.wm.app.b2b.server.ServiceException;
// --- <<IS-START-IMPORTS>> ---
import com.wm.lang.ns.NSName;
import com.wm.app.b2b.server.ns.Namespace;
import java.text.SimpleDateFormat;
import java.io.IOException;
import java.util.Date;
import java.util.Calendar;
import java.text.ParseException;
import java.text.ParsePosition;
import com.wm.app.b2b.server.Session;
import com.wm.app.b2b.server.InvokeState;
// --- <<IS-END-IMPORTS>> ---

public final class JavaServices

{
	// ---( internal utility methods )---

	final static JavaServices _instance = new JavaServices();

	static JavaServices _newInstance() { return new JavaServices(); }

	static JavaServices _cast(Object o) { return (JavaServices)o; }

	// ---( server methods )---




	public static final void addDateTime (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(addDateTime)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:optional inDateTime
		// [i] field:0:required pattern
		// [i] field:0:required datePart
		// [i] field:0:optional addValue
		// [i] field:0:optional subtractDay {"false","true"}
		// [o] field:0:optional outDateTime
		String outDateTime = null;
		IDataCursor idc = pipeline.getCursor();
		
		String inDateTimeString = IDataUtil.getString(idc, "inDateTime");
		if (inDateTimeString == null || inDateTimeString.trim().length() == 0) {
			idc.destroy();
			return;
		}
		String pattern = IDataUtil.getString(idc, "pattern");
		String datePart = IDataUtil.getString(idc, "datePart");
		String addValueString = IDataUtil.getString(idc, "addValue");
		// default to zero if no add value is passed
		if (addValueString == null || addValueString.trim().length() == 0) addValueString = "0";
		String subtractDay = IDataUtil.getString(idc, "subtractDay");
		// default to false if not passed
		if (subtractDay == null) subtractDay = "false";
		
		try {
			SimpleDateFormat sdf = new SimpleDateFormat(pattern);
			Calendar calendar = Calendar.getInstance();
			calendar.setTime(sdf.parse(inDateTimeString));
			int addValue = Integer.parseInt(addValueString);
		
			if (datePart.equals("yyyy")) {
				calendar.add(Calendar.YEAR, addValue);
			}
			else if (datePart.equals("MM")) {
				calendar.add(Calendar.MONTH, addValue);
			}
			else if (datePart.equals("dd")) {
				calendar.add(Calendar.DAY_OF_MONTH, addValue);
			}
			else if (datePart.equals("HH")) {
				calendar.add(Calendar.HOUR, addValue);
			}
			else if (datePart.equals("mm")) {
				calendar.add(Calendar.MINUTE, addValue);
			}
			else if (datePart.equals("ss")) {
				calendar.add(Calendar.SECOND, addValue);
			}
			// subtract a day if flag set
			if (subtractDay.equals("true")) {
				calendar.add(Calendar.DAY_OF_MONTH, -1);
			} 
			// format output
			outDateTime = sdf.format(calendar.getTime());
		}
		catch (Exception e) {
			throw new ServiceException(e);
		}
		
		// write out pipeline
		IDataUtil.put(idc, "outDateTime", outDateTime);
		idc.destroy();
		// --- <<IS-END>> ---

                
	}



	public static final void calculateDateDifference (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(calculateDateDifference)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required startDateTime
		// [i] field:0:required endDateTime
		// [i] field:0:required startDateFormat
		// [i] field:0:required endDateFormat
		// [o] field:0:required dateDifferenceSec
		// [o] field:0:required dateDifferenceMin
		// [o] field:0:required dateDifferenceHr
		// [o] field:0:required dateDifferenceDay
		// pipeline
		IDataCursor pipelineCursor = pipeline.getCursor();
		String	startDateTime = "";
		String	endDateTime = "";
		String startDateFormat = "";
		String endDateFormat = "";
		if (pipelineCursor.first("startDateTime"))
		{
			startDateTime = (String) pipelineCursor.getValue();
		}
		if (pipelineCursor.first("endDateTime"))
		{
			endDateTime = (String) pipelineCursor.getValue();
		}
		if (pipelineCursor.first("startDateFormat"))
		{
			startDateFormat = (String) pipelineCursor.getValue();
		}
		if (pipelineCursor.first("endDateFormat"))
		{
			endDateFormat = (String) pipelineCursor.getValue();
		}
		
		if (startDateTime.equals("") || endDateTime.equals(""))
			throw new ServiceException("Dates cannot be null");
		if (startDateFormat.equals("") || endDateFormat.equals(""))
			throw new ServiceException("Date formats cannot be null");
		
		pipelineCursor.destroy();
		
		try {
				SimpleDateFormat sdf = new SimpleDateFormat(startDateFormat);
				Date sdt = sdf.parse(startDateTime);
				SimpleDateFormat edf = new SimpleDateFormat(endDateFormat);
				Date edt = edf.parse(endDateTime);
				long  timediff = edt.getTime() - sdt.getTime();
		
		//		SimpleDateFormat ssdf = new SimpleDateFormat("HH:mm:ss");
		//		Calendar cal = Calendar.getInstance();
		//		cal.clear();
		//		cal.set(Calendar.SECOND, (int) timediff /1000);
		
		//		Date newDateTime = cal.getTime();
		//		String displayTime=null;
		
		//		if (cal.get(Calendar.DAY_OF_YEAR) > 1 )
		//		    displayTime = ssdf.format(newDateTime) + " and " + (cal.get(Calendar.DAY_OF_YEAR)-1) + " Day(s)" ;
		//		else 
		//		    displayTime = ssdf.format(newDateTime);
		
				String displayTimeSec = Long.toString(timediff/1000);
				String displayTimeMin = Long.toString(timediff/60000);
				String displayTimeHr = Long.toString(timediff/3600000);
				String displayTimeDay = Long.toString(timediff/86400000);
		
				// pipeline
				IDataCursor pipelineCursor_1 = pipeline.getCursor();
				pipelineCursor_1.last();
				pipelineCursor_1.insertAfter( "dateDifferenceSec", displayTimeSec);
				pipelineCursor_1.insertAfter( "dateDifferenceMin", displayTimeMin);
				pipelineCursor_1.insertAfter( "dateDifferenceHr", displayTimeHr);
				pipelineCursor_1.insertAfter( "dateDifferenceDay", displayTimeDay);
				pipelineCursor_1.destroy();
			} catch (ParseException e) {
				throw new ServiceException("Error parsing the date time: " + e);
			}
		// --- <<IS-END>> ---

                
	}



	public static final void compareDates (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(compareDates)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required dateOne
		// [i] field:0:required dateTwo
		// [i] field:0:required dateFormat
		// [i] field:0:required comparisonOperator {">","<","=",">=","<="}
		// [o] field:0:required comparisonResult
		// pipeline
		IDataCursor pipelineCursor = pipeline.getCursor();
		String dateOne = "";
		String dateTwo = "";
		String dateFormat = "";
		String comparisonOperator = "";
		if (pipelineCursor.first("dateOne"))
		{
			dateOne = (String) pipelineCursor.getValue();
		}
		if (pipelineCursor.first("dateTwo"))
		{
			dateTwo = (String) pipelineCursor.getValue();
		}
		if (pipelineCursor.first("dateFormat"))
		{
			dateFormat = (String) pipelineCursor.getValue();
		}
		if (pipelineCursor.first("comparisonOperator"))
		{
			comparisonOperator = (String) pipelineCursor.getValue();
		}
		
		//Handle empty inputs
		if (dateOne.equals("") || dateTwo.equals(""))
			throw new ServiceException("Both dates are required fields!");
		if (dateFormat.equals(""))
			throw new ServiceException("dateFormat is a required field!");
		if (comparisonOperator.equals(""))
			throw new ServiceException("comparisonOperator is a required field!");
		
		pipelineCursor.destroy();
		
			try {
				//get the dates
				SimpleDateFormat sdf = new SimpleDateFormat(dateFormat);
		
				Date dateDateOne = (Date)sdf.parse(dateOne);
				Date dateDateTwo = (Date)sdf.parse(dateTwo);
		
				String comparisonResult = "false";
				
				//compare the dates
				if (comparisonOperator.equals(">"))
				{
					if( dateDateOne.after(dateDateTwo) )
						comparisonResult = "true";
				}
				else if (comparisonOperator.equals("<"))
				{
					if( dateDateTwo.after(dateDateOne) )
						comparisonResult = "true";
				}
				else if (comparisonOperator.equals("="))
				{
					if( dateDateOne.equals(dateDateTwo) )
						comparisonResult = "true";
				}
				else if (comparisonOperator.equals(">="))
				{
					if( dateDateOne.after(dateDateTwo) || dateDateOne.equals(dateDateTwo) )
						comparisonResult = "true";
				}
				else if (comparisonOperator.equals("<="))
				{
					if( dateDateTwo.after(dateDateOne) || dateDateOne.equals(dateDateTwo) )
						comparisonResult = "true";
				}
		
				// pipeline
				IDataCursor pipelineCursor_1 = pipeline.getCursor();
				pipelineCursor_1.last();
				pipelineCursor_1.insertAfter( "comparisonResult", comparisonResult);
				pipelineCursor_1.destroy();
			} 
			catch (ParseException e) 
			{
				throw new ServiceException("Error: " + e);
			}
		// --- <<IS-END>> ---

                
	}



	public static final void invokeServiceThrowExceptions (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(invokeServiceThrowExceptions)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required service
		// [i] field:0:required interface
		// [i] record:0:required input
		// To access the data in the pipeline you must create a cursor
		// on the IData object.
		IDataCursor idcPipeline = pipeline.getCursor();
		Session session = Service.getSession();
		
		//Initialize variables
		String strServiceName = null;
		String strInterfaceName = null;
		
		// This try block performs multiple functions.  First it gets the data out of the 
		// pipeline.  It then builds calls
		// Service.doInvoke() method call.  The Service.doInvoke actually invokes the 
		// specified service and catches any errors that may be thrown in the process.
		try
		{	
			if (idcPipeline.first("service"))
			{
				strServiceName = (String)idcPipeline.getValue();
			}
			else
			{
				throw new ServiceException("Invalid service name");
			}
		
			if (idcPipeline.first("interface"))
			{
				strInterfaceName = (String)idcPipeline.getValue();
			}
			else
			{
				throw new ServiceException("Invalid service name");
			}
		
			if (strServiceName.length() == 0 || strInterfaceName.length() == 0)
				throw new ServiceException("Invalid service name");
			
			//execute the service specified passing the entire pipeline
			IData results = Service.doInvoke(strInterfaceName, strServiceName, session, pipeline);
			IDataUtil.merge(results, pipeline);
		}
		catch(Exception e)
		{
		     // Allow the error to bubble up.
		     throw new ServiceException(e);
		}
		finally
		{
			// Always destroy your cursors!!!
			idcPipeline.destroy();		
		}
		// --- <<IS-END>> ---

                
	}



	public static final void serviceExists (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(serviceExists)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required folderName
		// [i] field:0:required serviceName
		// [o] field:0:required Result
		IDataCursor pc = pipeline.getCursor(); 
		
		String strFolderName = ""; 
		String strServiceName = ""; 
		
		if(pc.first("folderName")) 
		strFolderName = (String)pc.getValue(); 
		
		if(pc.first("serviceName")) 
		strServiceName = (String)pc.getValue(); 
		
		String strResult = "False"; 
		
		NSName nsname = NSName.create(strFolderName,strServiceName); 
		Namespace namesp = Namespace.current(); 
		
		if( namesp.nodeExists(nsname)) 
		strResult = "True"; 
		
		pc.insertAfter("Result",strResult); 
		pc.destroy(); 
		// --- <<IS-END>> ---

                
	}



	public static final void sortDocumentList (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(sortDocumentList)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] record:1:required itemList
		// [i] field:0:required keyField
		// [i] field:0:required compareType {"COLLATION","TIME"}
		// [i] field:0:required sortDescending {"true","false"}
		// [i] field:0:optional compareDateFormat
		// [o] field:0:required sorted
		// [o] record:1:required itemList
		IData[] sortedItemList = null; 
		
		// pipeline 
		IDataCursor pipelineCursor = pipeline.getCursor(); 
		IData[] itemList = IDataUtil.getIDataArray( pipelineCursor, "itemList" ); 
		String keyField = IDataUtil.getString( pipelineCursor, "keyField" ); 
		boolean sortDescending = 
		(Boolean.valueOf(IDataUtil.getString( pipelineCursor, 
		"sortDescending" ))).booleanValue(); 
		String compareTypeRequested = IDataUtil.getString( pipelineCursor, 
		"compareType" );
		String compareDateFormat = IDataUtil.getString( pipelineCursor, 
		"compareDateFormat" );
		pipelineCursor.destroy(); 
		
		int compareType = IDataUtil.COMPARE_TYPE_COLLATION;
		if (compareTypeRequested.equals("TIME")) {
		   compareType = IDataUtil.COMPARE_TYPE_TIME;
		}
		
		if(itemList != null) 
		{ 
		sortedItemList = 
		IDataUtil.sortIDataArrayByKey(itemList, 
		keyField, 
		compareType, 
		compareDateFormat, 
		sortDescending);
		} 
		// pipeline 
		pipelineCursor = pipeline.getCursor(); 
		IDataUtil.put( pipelineCursor, 
		"sorted", sortedItemList==null ? "false" : "true"); 
		pipelineCursor.destroy();
		// --- <<IS-END>> ---

                
	}



	public static final void sortDocumentList_1 (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(sortDocumentList_1)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] record:1:required itemList
		// [i] field:0:required keyField
		// [i] field:0:required compareType {"COLLATION","TIME"}
		// [i] field:0:required sortDescending {"true","false"}
		// [i] field:0:optional compareDateFormat
		// [o] field:0:required sorted
		// [o] record:1:required itemList
		IData[] sortedItemList = null; 
		
		// pipeline 
		IDataCursor pipelineCursor = pipeline.getCursor(); 
		IData[] itemList = IDataUtil.getIDataArray( pipelineCursor, "itemList" ); 
		String keyField = IDataUtil.getString( pipelineCursor, "keyField" ); 
		boolean sortDescending = 
		(Boolean.valueOf(IDataUtil.getString( pipelineCursor, 
		"sortDescending" ))).booleanValue(); 
		String compareTypeRequested = IDataUtil.getString( pipelineCursor, 
		"compareType" );
		String compareDateFormat = IDataUtil.getString( pipelineCursor, 
		"compareDateFormat" );
		pipelineCursor.destroy(); 
		
		int compareType = IDataUtil.COMPARE_TYPE_COLLATION;
		if (compareTypeRequested.equals("TIME")) {
		   compareType = IDataUtil.COMPARE_TYPE_TIME;
		}
		
		if(itemList != null) 
		{ 
		sortedItemList = 
		IDataUtil.sortIDataArrayByKey(itemList, 
		keyField, 
		compareType, 
		compareDateFormat, 
		sortDescending);
		} 
		// pipeline 
		pipelineCursor = pipeline.getCursor(); 
		IDataUtil.put( pipelineCursor, 
		"sorted", sortedItemList==null ? "false" : "true"); 
		pipelineCursor.destroy();
		// --- <<IS-END>> ---

                
	}
}


```

### `GLDExpressWebServices.Utilities`

```java
package GLDExpressWebServices.Utilities;

// -----( IS Java Code Template v1.2
// -----( CREATED: 2008-09-08 13:48:51 EDT
// -----( ON-HOST: csc06dwmis01.keybank.com

import com.wm.data.*;
import com.wm.util.Values;
import com.wm.app.b2b.server.Service;
import com.wm.app.b2b.server.ServiceException;
// --- <<IS-START-IMPORTS>> ---
import com.keybank.kef.bop.model.*;
import com.keybank.kef.bop.*;
// --- <<IS-END-IMPORTS>> ---

public final class JavaServices

{
	// ---( internal utility methods )---

	final static JavaServices _instance = new JavaServices();

	static JavaServices _newInstance() { return new JavaServices(); }

	static JavaServices _cast(Object o) { return (JavaServices)o; }

	// ---( server methods )---




	public static final void doesLesseeMatch (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(doesLesseeMatch)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [o] field:0:required matched
		//	 pipeline
			IDataCursor pipelineCursor = pipeline.getCursor();
		
				// expressLinkCustomerData
				IData	expressLinkCustomerData = IDataUtil.getIData( pipelineCursor, "expressLinkCustomerData" );
				ExpressLinkCustomerData inExpressLinkCustomerData = null;
				if ( expressLinkCustomerData != null)
				{
					IDataCursor expressLinkCustomerDataCursor = expressLinkCustomerData.getCursor();
		
						// i.expressLinkCustomerData
						IData	expressLinkCustomerData_1 = IDataUtil.getIData( expressLinkCustomerDataCursor, "expressLinkCustomerData" );
						if ( expressLinkCustomerData_1 != null)
						{					
							IDataCursor expressLinkCustomerData_1Cursor = expressLinkCustomerData_1.getCursor();
								String	accountNumber = IDataUtil.getString( expressLinkCustomerData_1Cursor, "accountNumber" );
								String	routingNumber = IDataUtil.getString( expressLinkCustomerData_1Cursor, "routingNumber" );
								String	remitCode = IDataUtil.getString( expressLinkCustomerData_1Cursor, "remitCode" );
								String	active = IDataUtil.getString( expressLinkCustomerData_1Cursor, "active" );
		
								inExpressLinkCustomerData = new ExpressLinkCustomerData();
								inExpressLinkCustomerData.setAccountNumber(accountNumber);
								inExpressLinkCustomerData.setRoutingNumber(routingNumber);
								inExpressLinkCustomerData.setRemitCode(remitCode);
								
								// i.dbaNames
								IData	dbaNames = IDataUtil.getIData( expressLinkCustomerData_1Cursor, "dbaNames" );
								if ( dbaNames != null)
								{
									IDataCursor dbaNamesCursor = dbaNames.getCursor();
										String[]	dbaName = IDataUtil.getStringArray( dbaNamesCursor, "dbaName" );
										if (dbaName != null) {
											for (int idx=0;idx<dbaName.length;idx++) {
												inExpressLinkCustomerData.addDbaName(dbaName[idx]);
											}
										}
									dbaNamesCursor.destroy();
								}
		
								// i.billings
								IData	billings = IDataUtil.getIData( expressLinkCustomerData_1Cursor, "billings" );
								if ( billings != null)
								{
									IDataCursor billingsCursor = billings.getCursor();
		
										// i.billing
										IData[]	billing = IDataUtil.getIDataArray( billingsCursor, "billing" );
										if ( billing != null)
										{
											for ( int i = 0; i < billing.length; i++ )
											{
												IDataCursor billingCursor = billing[i].getCursor();
													String	name = IDataUtil.getString( billingCursor, "name" );
													String	address1 = IDataUtil.getString( billingCursor, "address1" );
													String	address2 = IDataUtil.getString( billingCursor, "address2" );
													String	city = IDataUtil.getString( billingCursor, "city" );
													String	state = IDataUtil.getString( billingCursor, "state" );
													String	zip = IDataUtil.getString( billingCursor, "zip" );
													String	billingActive = IDataUtil.getString( billingCursor, "active" );
		
													inExpressLinkCustomerData.addBilling(name, address1, address2, city, state, zip, Boolean.valueOf(billingActive).booleanValue());
													
													billingCursor.destroy();
											}
										}
									billingsCursor.destroy();
								}
		
							expressLinkCustomerData_1Cursor.destroy();
						}
					expressLinkCustomerDataCursor.destroy();
				}
		
				// leasePakLesseeData
				IData	leasePakLesseeData = IDataUtil.getIData( pipelineCursor, "leasePakLesseeData" );
				LeasePakLesseeData lpkd = null;
				if ( leasePakLesseeData != null)
				{
					IDataCursor leasePakLesseeDataCursor = leasePakLesseeData.getCursor();
		
						// i_2.LeasePakLesseeData
						IData	LeasePakLesseeData = IDataUtil.getIData( leasePakLesseeDataCursor, "LeasePakLesseeData" );
						if ( LeasePakLesseeData != null)
						{
							IDataCursor LeasePakLesseeDataCursor = LeasePakLesseeData.getCursor();
								String	dbaName_1 = IDataUtil.getString( LeasePakLesseeDataCursor, "dbaName" );
								String	remitCode_1 = IDataUtil.getString( LeasePakLesseeDataCursor, "remitCode" );
								String	accountNumber_1 = IDataUtil.getString( LeasePakLesseeDataCursor, "accountNumber" );
								String	routingNumber_1 = IDataUtil.getString( LeasePakLesseeDataCursor, "routingNumber" );
								String	lesseeName = IDataUtil.getString( LeasePakLesseeDataCursor, "lesseeName" );
								String	lesseeAddress1 = IDataUtil.getString( LeasePakLesseeDataCursor, "lesseeAddress1" );
								String	lesseeAddress2 = IDataUtil.getString( LeasePakLesseeDataCursor, "lesseeAddress2" );
								String	lesseeCity = IDataUtil.getString( LeasePakLesseeDataCursor, "lesseeCity" );
								String	lesseeState = IDataUtil.getString( LeasePakLesseeDataCursor, "lesseeState" );
								String	lesseeZip = IDataUtil.getString( LeasePakLesseeDataCursor, "lesseeZip" );
								String	billingName = IDataUtil.getString( LeasePakLesseeDataCursor, "billingName" );
								String	billingAddress1 = IDataUtil.getString( LeasePakLesseeDataCursor, "billingAddress1" );
								String	billingAddress2 = IDataUtil.getString( LeasePakLesseeDataCursor, "billingAddress2" );
								String	billingCity = IDataUtil.getString( LeasePakLesseeDataCursor, "billingCity" );
								String	billingState = IDataUtil.getString( LeasePakLesseeDataCursor, "billingState" );
								String	billingZip = IDataUtil.getString( LeasePakLesseeDataCursor, "billingZip" );
								
								lpkd = new LeasePakLesseeData(dbaName_1, remitCode_1,accountNumber_1, routingNumber_1, 
										lesseeName, lesseeAddress1,lesseeAddress2, 
										lesseeCity, lesseeState, lesseeZip,
										billingName, billingAddress1,billingAddress2, 
										billingCity, billingState, billingZip);
							LeasePakLesseeDataCursor.destroy();
						}
					leasePakLesseeDataCursor.destroy();
				}
			pipelineCursor.destroy();
		
			boolean result = false;
			if ((inExpressLinkCustomerData != null) && (lpkd != null)) {
					// result = (new LesseeMatcher()).match(inExpressLinkCustomerData, lpkd);
					result = match(inExpressLinkCustomerData, lpkd);
					//String results = doTheyMatch(inExpressLinkCustomerData, lpkd);
					//if (results == null) result = true;
		                        //	else { result = false; throw new ServiceException("Does not match: "+results); }
					}
			else throw new ServiceException("ExpressLinkCustomerData or LeasePakLesseeData is null. "+
					" (ExpressLinkCustomerData: "+inExpressLinkCustomerData + " - LeasePakLesseeData: "+lpkd);
			
		//	 pipeline
			IDataCursor pipelineCursor_1 = pipeline.getCursor();
			IDataUtil.put( pipelineCursor_1, "matched", ""+result );
			pipelineCursor_1.destroy();
		// --- <<IS-END>> ---

                
	}

	// --- <<IS-START-SHARED>> ---
	public static boolean match(ExpressLinkCustomerData xlData, LeasePakLesseeData lpData) {
		ExpressLinkCustomerBillingData xlBillingData = (ExpressLinkCustomerBillingData) xlData.getBillings().get(0);
		
 		if (lpData.useLesseeInfo()) {
			if (!isEqualinXML(xlBillingData.getName(),lpData.getLesseeName())) return false;
			if (!isEqualinXML(xlBillingData.getAddress1(), lpData.getLesseeAddress1())) return false;
			if (!isEqualinXML(xlBillingData.getAddress2(), lpData.getLesseeAddress2())) return false;
			if (!isEqualinXML(xlBillingData.getCity(), lpData.getLesseeCity())) return false;
			if (!isEqualinXML(xlBillingData.getState(), lpData.getLesseeState())) return false;
			if (!isEqualinXML(xlBillingData.getZip(), lpData.getLesseeZip())) return false;
		} else {
			if (!isEqualinXML(xlBillingData.getName(), lpData.getBillingName())) return false;
			if (!isEqualinXML(xlBillingData.getAddress1(), lpData.getBillingAddress1())) return false;
			if (!isEqualinXML(xlBillingData.getAddress2(), lpData.getBillingAddress2())) return false;
			if (!isEqualinXML(xlBillingData.getCity(), lpData.getBillingCity())) return false;
			if (!isEqualinXML(xlBillingData.getState(), lpData.getBillingState())) return false;
			if (!isEqualinXML(xlBillingData.getZip(), lpData.getBillingZip())) return false;
		}
		
		if (!(isEqualinXML(xlData.getAccountNumber(), lpData.getAccountNumber()) && isEqualinXML(xlData.getRoutingNumber(), lpData.getRoutingNumber()))) return false;
		
		if (!isEqualinXML(xlData.getRemitCode(), lpData.getRemitCode())) return false;
		
		if (!isEqualinXML(xlData.getDbaName(), lpData.getDbaName())) return false;
		return true;
	}
	
	public static   String doTheyMatch(ExpressLinkCustomerData xlData, LeasePakLesseeData lpData) {
		ExpressLinkCustomerBillingData xlBillingData = (ExpressLinkCustomerBillingData) xlData.getBillings().get(0);
		StringBuffer sb = new StringBuffer();
 		if (lpData.useLesseeInfo()) { 
 			sb.append(isEqualMessage(xlBillingData.getName(),lpData.getLesseeName(),"Billing Name"));
 			sb.append(isEqualMessage(xlBillingData.getAddress1(), lpData.getLesseeAddress1(),"Addr 1"));
 			sb.append(isEqualMessage(xlBillingData.getAddress2(), lpData.getLesseeAddress2(),"Addr 2"));			
 			sb.append(isEqualMessage(xlBillingData.getState(), lpData.getLesseeState(),"State"));
 			sb.append(isEqualMessage(xlBillingData.getZip(), lpData.getLesseeZip(),"Zip"));
		} else {
			sb.append(isEqualMessage(xlBillingData.getName(), lpData.getBillingName(),"Billing Name"));
			sb.append(isEqualMessage(xlBillingData.getAddress1(), lpData.getBillingAddress1(),"Billing Addr1"));
			sb.append(isEqualMessage(xlBillingData.getAddress2(), lpData.getBillingAddress2(),"Billing Addr2"));
			sb.append(isEqualMessage(xlBillingData.getCity(), lpData.getBillingCity(),"Billing City"));
			sb.append(isEqualMessage(xlBillingData.getState(), lpData.getBillingState(),"Billing State"));
			sb.append(isEqualMessage(xlBillingData.getZip(), lpData.getBillingZip(),"Billing Zip"));
		}
		
 		sb.append(isEqualMessage(xlData.getAccountNumber(), lpData.getAccountNumber(),"Account Number"));
 		sb.append(isEqualMessage(xlData.getRoutingNumber(), lpData.getRoutingNumber(),"Routing Number"));
		
 		sb.append(isEqualMessage(xlData.getRemitCode(), lpData.getRemitCode(),"Remit Code"));
		
 		sb.append(isEqualMessage(xlData.getDbaName(), lpData.getDbaName(),"DBAName"));
 		if (sb.length() > 0) return sb.toString();
		return null;
	}

	private static String isEqualMessage(String xos, String lpk,String fieldName) {
		if (!isEqualinXML(xos,lpk)) return fieldName +" does not match: [xos:"+xos+"]!=[lpk:"+lpk+"]\n";
		return "";
	}
	
	protected static boolean isEqualinXML(String a, String b) {
		if (a == b) {
			return true;
		}
		if (a == null) a = "";
		if (b == null) b = "";
		return a.equals(b);
	}
	// --- <<IS-END-SHARED>> ---
}


```

### `GLDSoap.Utilities`

```java
package GLDSoap.Utilities;

// -----( IS Java Code Template v1.2
// -----( CREATED: 2008-06-19 12:03:38 EDT
// -----( ON-HOST: cwb02dwmis02.keybank.com

import com.wm.data.*;
import com.wm.util.Values;
import com.wm.app.b2b.server.Service;
import com.wm.app.b2b.server.ServiceException;
// --- <<IS-START-IMPORTS>> ---
import java.util.*;
// --- <<IS-END-IMPORTS>> ---

public final class JavaServices

{
	// ---( internal utility methods )---

	final static JavaServices _instance = new JavaServices();

	static JavaServices _newInstance() { return new JavaServices(); }

	static JavaServices _cast(Object o) { return (JavaServices)o; }

	// ---( server methods )---




	public static final void addNameSpace (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(addNameSpace)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required nodeName
		// [i] field:0:required nameSpace
		// [i] field:0:optional prefix
		// [i] record:0:required document
		// [o] record:0:required document
   // Get pipeline data   
    IDataCursor idc = pipeline.getCursor();
    String namespace = IDataUtil.getString( idc, "nameSpace" );
    String nodeName = IDataUtil.getString( idc, "nodeName" );
    String prefix = IDataUtil.getString( idc, "prefix" );
    IData outputDoc = IDataUtil.getIData( idc, "document" );  
    IDataCursor docCursor = null; 
  
    if ( namespace == null || outputDoc == null || nodeName == null ) {
        throw new ServiceException( "nameSpace, nodeName and document are required" );
    }

    try { 
        docCursor = outputDoc.getCursor(); 
        IData node = IDataUtil.getIData( docCursor, nodeName );
        if ( node != null ) {
            IDataCursor nodeCursor = node.getCursor();
            if ( prefix != null ) {
	    	nodeCursor.insertBefore( "@xmlns:" + prefix , namespace );
            }
            else {
	        nodeCursor.insertBefore( "@xmlns", namespace );
            }
	    nodeCursor.destroy();
        }
        else {
            throw new ServiceException( "Cannot find node " + nodeName );
        }
                       
        idc.setValue( outputDoc ); 
    }	      
    catch ( Exception e ) {
        throw new ServiceException( e );
    }
    finally {
	if ( null != docCursor ) docCursor.destroy();
	if ( null != idc ) idc.destroy();
    }	
		// --- <<IS-END>> ---

                
	}



	public static final void getNodeName (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(getNodeName)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] record:0:required document
		// [o] field:0:required nodeName
		// [o] field:0:required prefix
    // Get pipeline data
    IDataCursor idc = pipeline.getCursor();
    IData document = IDataUtil.getIData( idc, "document" );
    
    if ( document != null ) {
       IDataCursor cursor = document.getCursor();
       cursor.first();
       String nodeName = cursor.getKey();
       String prefix = null;
       
       // Check for prefix in node name
       String [] nodeParts = nodeName.split(":");
       if ( nodeParts.length == 2 ) {
           nodeName = nodeParts[1];
           prefix = nodeParts[0];
       }

       idc.last();        
       idc.insertAfter( "nodeName", nodeName );
       idc.insertAfter( "prefix", prefix );

       cursor.destroy();
    }
    idc.destroy();
 

		// --- <<IS-END>> ---

                
	}
}


```
