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
