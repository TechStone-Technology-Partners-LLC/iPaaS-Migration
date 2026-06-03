package GLDExpressGateway.Utilities;

// -----( IS Java Code Template v1.2
// -----( CREATED: 2008-06-28 11:29:21 EDT
// -----( ON-HOST: cwb02dwmis02.keybank.com

import com.wm.data.*;
import com.wm.util.Values;
import com.wm.app.b2b.server.Service;
import com.wm.app.b2b.server.ServiceException;
// --- <<IS-START-IMPORTS>> ---
import com.wm.lang.ns.NSName;
import com.wm.app.b2b.server.ns.Namespace;
import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.MultiThreadedHttpConnectionManager;
import org.apache.commons.httpclient.methods.PostMethod;
import java.io.IOException;
import org.apache.commons.httpclient.methods.StringRequestEntity;
import org.apache.commons.httpclient.Credentials;
import org.apache.commons.httpclient.HttpState;
import org.apache.commons.httpclient.auth.AuthScope;
import org.apache.commons.httpclient.UsernamePasswordCredentials;
import java.text.SimpleDateFormat;
import java.text.ParseException;
import java.util.*;
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



	public static final void httpWithSession (IData pipeline)
        throws ServiceException
	{
		// --- <<IS-START(httpWithSession)>> ---
		// @subtype unknown
		// @sigtype java 3.5
		// [i] field:0:required url
		// [i] field:0:optional content
		// [i] field:2:optional parameters
		// [i] record:0:optional auth
		// [i] - field:0:required pass
		// [i] - field:0:required user
		// [o] field:0:required response
		IDataCursor pipelineCursor = pipeline.getCursor(); 
		
		PostMethod httpPost = null;
		try {
		    String url = IDataUtil.getString( pipelineCursor, "url");
		    if (!url.startsWith("http")) {
		        throw new ServiceException("Invalid url provided as input - can not do http post.");
		    } 
		    httpPost = new PostMethod(url);
		    
		    // set up credentials if applicable
		    IData auth = IDataUtil.getIData(pipelineCursor, "auth");
		    if (auth != null) {
		    	IDataCursor authCursor = auth.getCursor();
		        String user = IDataUtil.getString( authCursor, "user");
		        String pass = IDataUtil.getString( authCursor, "pass");
		        if (user != null && user.trim().length() > 0 
		        		&& pass != null && pass.trim().length() > 0) {
		        	Credentials credentials = new UsernamePasswordCredentials(user, pass);
		        	HttpState httpState = new HttpState();
		    		httpState.setCredentials(AuthScope.ANY, credentials);
		    		CLIENT.setState(httpState);
		        }
		    }
		
		    String[][] parameters = IDataUtil.getStringTable(pipelineCursor, "parameters");
		    if (parameters != null && parameters.length > 0) {
		        for (int i = 0; i < parameters.length; i++) {
		            if (parameters[i].length != 2) {
		                throw new ServiceException("Invalid parameter input for: " + parameters[i][0] 
		                      + ". Table width too wide (" + parameters[i].length + ").");
			    }
		
		            httpPost.setParameter(parameters[i][0], parameters[i][1]);
		        }
		    } else {
		        // This is fine there no parameters can be valid.
		    }
		
		    String content = IDataUtil.getString( pipelineCursor, "content");
		    if (content != null) {
		        // change this later to allow for different content types
		        httpPost.setRequestEntity(new StringRequestEntity(pipelineCursor.getKey(), "text/xml", "ISO-8859-1"));
		    }
		
		    CLIENT.executeMethod(httpPost);
		
		    IDataUtil.put(pipelineCursor, "response", httpPost.getResponseBodyAsString());
		    pipelineCursor.destroy();  
		
		} catch (IOException e) {
		    // Error with stack trace
		    throw new ServiceException(e);
		} finally {
		    if (httpPost != null) {
		        httpPost.releaseConnection();
		    }
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
		// [i] field:0:required sortDescending
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
		pipelineCursor.destroy(); 
		
		if(itemList != null) 
		{ 
		sortedItemList = 
		IDataUtil.sortIDataArrayByKey(itemList, 
		keyField, 
		IDataUtil.COMPARE_TYPE_COLLATION, 
		null, 
		sortDescending); 
		} 
		// pipeline 
		pipelineCursor = pipeline.getCursor(); 
		IDataUtil.put( pipelineCursor, 
		"sorted", sortedItemList==null ? "false" : "true"); 
		pipelineCursor.destroy();
		// --- <<IS-END>> ---

                
	}

	// --- <<IS-START-SHARED>> ---
	private static final HttpClient CLIENT = new HttpClient(new MultiThreadedHttpConnectionManager());
	/**
	 *  return the true offset in millisecond of the default time zone
	 */
	private static int getOffset()
	{
		//SimpleTimeZone tz = (SimpleTimeZone) SimpleTimeZone.getDefault();
		TimeZone tz = SimpleTimeZone.getDefault();
	    return tz.getRawOffset() + tz.getDSTSavings(); 
	}
	
	
	/**
	 *  format the offset millis as hh:mm 
	 */
	private static String formatOffset(int offset)
	{
			int lOffset = offset;			
	        String sign = "+";
	        if ( lOffset < 0 )
	        {
	            sign = "-";
	            lOffset = -lOffset;
	        }
	        int offsetHour = lOffset / 3600000;
	        int offsetMin = (lOffset - offsetHour * 3600000)/60000;
			
			return sign + pad2Digits(offsetHour) + ":" + pad2Digits(offsetMin);  
	}
	
	/**
	 *  pad left for 2 digit number , e.g "03"
	 */
	private static String pad2Digits(int num)
	{
		String res;
		if (num < 10)
	    {
	        res = "0" + num;
	    }
		else
		{
			res = String.valueOf(num);
		}
		return res;
	}
	// --- <<IS-END-SHARED>> ---
}

