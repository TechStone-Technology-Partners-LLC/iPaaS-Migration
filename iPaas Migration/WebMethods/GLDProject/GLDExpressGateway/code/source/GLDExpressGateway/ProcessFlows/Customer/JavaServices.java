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

