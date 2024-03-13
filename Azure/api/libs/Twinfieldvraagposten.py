import pandas as pd
import requests as r
import xml.etree.ElementTree as ET
import time
from azure.data.tables import TableServiceClient

soapvraagposten =	f"""<column id="3">
											<field>fin.trs.head.code</field>
											<label>Transaction type</label>
											<visible>true</visible>
											<ask>true</ask>
											<operator>equal</operator>
											<from></from>
                                            <to></to>
										</column>
                                        <column id="5">
											<field>fin.trs.line.dim1</field>
											<label>General ledger acct.</label>
											<visible>false</visible>
											<ask>true</ask>
											<operator>between</operator>
											<from>219000</from>
											<to>219000</to>
										</column>
										<column id="51">
											<field>fin.trs.head.reportingstructure</field>
											<label>Reporting structure</label>
											<visible>false</visible>
											<ask>true</ask>
											<operator>equal</operator>
											<from></from>
											<to></to>
										</column>
										<!-- Other fields that are shown in the report -->
										<column id="2">
											<field>fin.trs.head.officename</field>
											<label>Company name</label>
											<visible>true</visible>
										</column>
										<column id="4">
											<field>fin.trs.head.year</field>
											<label>Year</label>
											<visible>true</visible>
										</column>
										<column id="5">
											<field>fin.trs.head.period</field>
											<label>Period</label>
											<visible>true</visible>
										</column>
										<column id="6">
											<field>fin.trs.head.number</field>
											<label>Transaction number</label>
											<visible>true</visible>
										</column>
										<column id="7">
											<field>fin.trs.head.date</field>
											<label>Trans. date</label>
											<visible>true</visible>
										</column>
										<column id="8">
											<field>fin.trs.line.dim1name</field>
											<label>General ledger acct. name</label>
											<visible>true</visible>
										</column>
										<column id="9">
											<field>fin.trs.line.valuesigned</field>
											<label>Amount</label>
											<visible>true</visible>
										</column>
										<column id="10">
											<field>fin.trs.line.basevaluesigned</field>
											<label>Base value</label>
											<visible>true</visible>
										</column>
										<column id="11">
											<field>fin.trs.line.description</field>
											<label>Description</label>
											<visible>true</visible>
										</column>
									</columns>
								</twinfield:xmlRequest>
							</twinfield:ProcessXmlDocument>
						</soap:Body>
					</soap:Envelope>"""


def getdata():

	tw_validate_token = "https://login.twinfield.com/auth/authentication/connect/accesstokenvalidation?token="
	tw_renew_token = "https://login.twinfield.com/auth/authentication/connect/token"
	tw_refresh_token = "b46a34d9d4a2386d75a9c177e42f2520"
	webservice = "https://api.accounting.twinfield.com/webservices/processxml.asmx?wsdl="

			
				# Header for requests
	headers = {
							'Content-Type': 'application/x-www-form-urlencoded',
							'Authorization': 'Basic VVBUV0lOQVBQOm5iaWRHcDhQNzZCa0hEU2NSdCtMcjFML2g2MG54eURoVWc9PQ==',
							'Cookie': 'culture=nl-NL'
							}

	# Payload for requests
	payload='grant_type=refresh_token&refresh_token=b46a34d9d4a2386d75a9c177e42f2520'

	# Post request for token renewal
	renewal = r.request("POST", tw_renew_token, headers=headers, data=payload)

	# Access token
	access_token = renewal.json()['access_token']
				


				# Access token validation
	validation = r.request("GET", tw_validate_token + access_token, headers=headers)

		

	

				
	body = f"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:twinfield="http://www.twinfield.com/">
											<soap:Header>
													<twinfield:Header>
														<twinfield:AccessToken>"""+access_token+"""</twinfield:AccessToken>
														<twinfield:CompanyCode>48903</twinfield:CompanyCode>
													</twinfield:Header>
												</soap:Header>
												<soap:Body>
													<twinfield:ProcessXmlDocument>
														<twinfield:xmlRequest>
															<columns code="030_1">
																<!-- Set the criteria for the report -->
																<column id="5">
																	<field>fin.trs.head.yearperiod</field>
																	<label>Year/period (YYYY/PP)</label>
																	<visible>false</visible>
																	<ask>true</ask>
																	<operator>between</operator>
																	<from>2023/00</from>
																	<to>2023/55</to>
																</column>"""+soapvraagposten
			
	# Header post request SOAP Envelope
	

	post_header = {
								"Content-Type" : "text/xml",
								"SOAPAction"   : "http://www.twinfield.com/ProcessXmlDocument" 
								}

	# Post request SOAP Envelope 030_3
	xml = (r.request("POST", url=webservice, headers=post_header, data=body))
			
	# XML file
	root = ET.fromstring(xml.text)

	# Find header elements
	th_elements = root.findall(".//th//td")
	th_text_list = []

	# Append header elements to list
	for th_element in th_elements:
		th_text_list.append(th_element.text)

	# Find data elements
	tr_elements = root.findall(".//tr//td")
	tr_text_list = []

	# Append data elements to list
	for tr_element in tr_elements:
		tr_text_list.append(tr_element.text)

	rows = [[]]

	# Loop over the original list and append each element to the appropriate sublist
	for i, element in enumerate(tr_text_list):
		sublist_index = i % 10
		if sublist_index == 0 and i != 0:
			rows.append([])
		rows[-1].append(element)

			# Create DataFrame
	
	service = TableServiceClient.from_connection_string(conn_str="UseDevelopmentStorage=true")
	try:
		client = service.create_table(table_name="vraagposten2023")
	except:
		client = service.get_table_client(table_name="vraagposten2023")
	
	for i, row in enumerate(rows):
		pKey = u"2023"
		entity = {
			u'PartitionKey':pKey,
			u'RowKey': str(i),
			u'head_code':row[0],
			u'head_officename':row[1],
			u'head_year':row[2],
			u'head_period':row[3],
			u'head_number':row[4],
			u'head_date':row[5],
			u'line_dim1name':row[6],
			u'line_valuesigned':row[7],
			u'line_basevaluesigned':row[8],
			u'line_description':row[9]
		}
		client.upsert_entity(entity)

getdata()
	#dir = (r'C:\Users\nicku\UP Events\UP Financien, Admin, HR Site - Documenten\Financien\Rapportages\Twinfieldvraagposten2023.xlsx')
			
	#df = pd.DataFrame(rows, columns=th_text_list)
	#df.to_excel(dir)
	#mytime = time.ctime()
			

	#print("Last version of excel is made "+mytime)

	#time.sleep(3600)

