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

