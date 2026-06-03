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

