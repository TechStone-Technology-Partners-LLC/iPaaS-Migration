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

