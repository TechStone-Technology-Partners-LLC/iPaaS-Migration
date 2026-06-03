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

