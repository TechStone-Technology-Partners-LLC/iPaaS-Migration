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

