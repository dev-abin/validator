<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ns0="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes" xmlns:ns2="http://www.w3.org/2000/09/xmldsig#" xmlns:ns3="http://www.iata.org/IATA/2015/EASD/00/AMA_AugmentationPoint" xmlns:ns4="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage" version="1.0">
	<xsl:template match="/">
		<ns4:IATA_OrderViewRS>
			<ns4:Response>
				<ns0:DataLists>
					<ns0:BaggageAllowanceList>
						<xsl:for-each select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:BaggageAllowanceList/ns0:BaggageAllowance">
							<ns0:BaggageAllowance>
								<xsl:for-each select="ns0:ApplicablePartyText">
									<ns0:ApplicablePartyText>
										<xsl:value-of select="."/>
									</ns0:ApplicablePartyText>
								</xsl:for-each>
								<xsl:copy-of select="ns0:BDC"/>
								<xsl:for-each select="ns0:BaggageAllowanceID">
									<ns0:BaggageAllowanceID>
										<xsl:value-of select="."/>
									</ns0:BaggageAllowanceID>
								</xsl:for-each>
								<xsl:for-each select="ns0:DescText">
									<ns0:DescText>
										<xsl:value-of select="."/>
									</ns0:DescText>
								</xsl:for-each>
								<xsl:for-each select="ns0:MaximumDimensionAllowance">
									<ns0:MaximumDimensionAllowance>
										<ns0:LinearMeasure>
											<xsl:value-of select="ns0:LinearMeasure"/>
										</ns0:LinearMeasure>
										<ns0:LengthUnitOfMeasurement>
											<xsl:value-of select="ns0:LengthUnitOfMeasurement"/>
										</ns0:LengthUnitOfMeasurement>
									</ns0:MaximumDimensionAllowance>
								</xsl:for-each>
								<xsl:copy-of select="ns0:PieceAllowance"/>
								<ns0:TypeCode>
									<xsl:value-of select="ns0:TypeCode"/>
								</ns0:TypeCode>
								<ns0:WeightAllowance>
									<ns0:TotalMaximumWeightMeasure>
										<xsl:value-of select="ns0:WeightAllowance/ns0:MaximumWeightMeasure"/>
									</ns0:TotalMaximumWeightMeasure>
									<ns0:WeightUnitOfMeasurement>
										<xsl:value-of select="ns0:WeightAllowance/ns0:WeightUnitOfMeasurement"/>
									</ns0:WeightUnitOfMeasurement>
								</ns0:WeightAllowance>
							</ns0:BaggageAllowance>
						</xsl:for-each>
					</ns0:BaggageAllowanceList>
					<xsl:copy-of select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:BaggageDisclosureList"/>
					<xsl:copy-of select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:ContactInfoList"/>
					<xsl:copy-of select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:DatedMarketingSegmentList"/>
					<xsl:copy-of select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:DatedOperatingLegList"/>
					<ns0:DatedOperatingSegmentList>
						<xsl:for-each select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:DatedOperatingSegmentList/ns0:DatedOperatingSegment">
							<ns0:DatedOperatingSegment>
								<xsl:for-each select="ns0:DatedOperatingLegRefID">
									<ns0:DatedOperatingLegRefID>
										<xsl:value-of select="."/>
									</ns0:DatedOperatingLegRefID>
								</xsl:for-each>
								<xsl:for-each select="ns0:DatedOperatingSegmentId">
									<ns0:DatedOperatingSegmentId>
										<xsl:value-of select="."/>
									</ns0:DatedOperatingSegmentId>
								</xsl:for-each>
								<ns0:CarrierDesigCode>
									<xsl:value-of select="ns0:CarrierDesigCode"/>
								</ns0:CarrierDesigCode>
								<ns0:CarrierName>
									<xsl:value-of select="ns0:CarrierName"/>
								</ns0:CarrierName>
								<ns0:DisclosureRefID>
									<xsl:value-of select="ns0:DisclosureRefID"/>
								</ns0:DisclosureRefID>
								<ns0:OperatingCarrierFlightNumberText>
									<xsl:value-of select="ns0:OperatingCarrierFlightNumberText"/>
								</ns0:OperatingCarrierFlightNumberText>
							</ns0:DatedOperatingSegment>
						</xsl:for-each>
					</ns0:DatedOperatingSegmentList>
					<ns0:DisclosureList>
						<xsl:for-each select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:DisclosureList/ns0:Disclosure">
							<xsl:copy-of select="."/>
						</xsl:for-each>
					</ns0:DisclosureList>
					<ns0:OriginDestList>
						<xsl:for-each select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:OriginDestList/ns0:OriginDest">
							<ns0:OriginDest>
								<ns0:DestCode>
									<xsl:value-of select="ns0:DestCode"/>
								</ns0:DestCode>
								<ns0:OriginCode>
									<xsl:value-of select="ns0:OriginCode"/>
								</ns0:OriginCode>
								<ns0:OriginDestID>
									<xsl:value-of select="ns0:OriginDestID"/>
								</ns0:OriginDestID>
								<ns0:PaxJourneyRefID>
									<xsl:value-of select="ns0:PaxJourneyRefID"/>
								</ns0:PaxJourneyRefID>
							</ns0:OriginDest>
						</xsl:for-each>
					</ns0:OriginDestList>
					<ns0:PaxJourneyList>
						<xsl:copy-of select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:PaxJourneyList/ns0:PaxJourney"/>
					</ns0:PaxJourneyList>
					<ns0:PaxList>
						<xsl:copy-of select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:PaxList/ns0:Pax"/>
					</ns0:PaxList>
					<ns0:PaxSegmentList>
						<xsl:for-each select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:PaxSegmentList/ns0:PaxSegment">
							<ns0:PaxSegment>
								<xsl:for-each select="ns0:PaxSegmentID">
									<ns0:PaxSegmentID>
										<xsl:value-of select="."/>
									</ns0:PaxSegmentID>
								</xsl:for-each>
								<ns0:DatedMarketingSegmentRefId>
									<xsl:value-of select="ns0:DatedMarketingSegmentRefId"/>
								</ns0:DatedMarketingSegmentRefId>
							</ns0:PaxSegment>
						</xsl:for-each>
					</ns0:PaxSegmentList>
					<ns0:PriceClassList>
						<xsl:for-each select="ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:PriceClassList/ns0:PriceClass">
							<ns0:PriceClass>
								<ns0:Code>
									<xsl:value-of select="ns0:Code"/>
								</ns0:Code>
								<xsl:copy-of select="ns0:Desc"/>
								<ns0:Name>
									<xsl:value-of select="ns0:Name"/>
								</ns0:Name>
								<ns0:PriceClassID>
									<xsl:value-of select="ns0:PriceClassID"/>
								</ns0:PriceClassID>
							</ns0:PriceClass>
						</xsl:for-each>
					</ns0:PriceClassList>
					<ns0:SeatProfileList>
						<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:SeatProfileList/ns0:SeatProfile">
							<ns0:SeatProfile>
								<ns0:SeatProfileID>
									<xsl:value-of select="ns0:SeatProfileID"/>
								</ns0:SeatProfileID>
							</ns0:SeatProfile>
						</xsl:for-each>
					</ns0:SeatProfileList>
					<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:DataLists/ns0:ServiceDefinitionList">
						<ns0:ServiceDefinitionList>
							<xsl:for-each select="ns0:ServiceDefinition">
								<ns0:ServiceDefinition>
									<ns0:ServiceCode>
										<xsl:value-of select="ns0:ServiceCode"/>
									</ns0:ServiceCode>
									<xsl:copy-of select="ns0:Desc"/>
									<xsl:for-each select="ns0:Name">
										<ns0:Name>
											<xsl:value-of select="."/>
										</ns0:Name>
									</xsl:for-each>
									<xsl:for-each select="ns0:OwnerCode">
										<ns0:OwnerCode>
											<xsl:value-of select="."/>
										</ns0:OwnerCode>
									</xsl:for-each>
									<xsl:for-each select="ns0:BookingInstructions">
										<ns0:BookingInstructions>
											<xsl:for-each select="ns0:MethodText">
												<ns0:MethodText>
													<xsl:value-of select="."/>
												</ns0:MethodText>
											</xsl:for-each>
											<xsl:for-each select="ns0:SpecialService">
												<ns0:SpecialService>
													<xsl:for-each select="ns0:SpecialServiceCode">
														<ns0:SpecialServiceCode>
															<xsl:value-of select="."/>
														</ns0:SpecialServiceCode>
													</xsl:for-each>
												</ns0:SpecialService>
											</xsl:for-each>
										</ns0:BookingInstructions>
									</xsl:for-each>
									<xsl:for-each select="ns0:RFIC">
										<ns0:RFIC>
											<xsl:value-of select="."/>
										</ns0:RFIC>
									</xsl:for-each>
									<xsl:for-each select="ns0:RFISC">
										<ns0:RFISC>
											<xsl:value-of select="."/>
										</ns0:RFISC>
									</xsl:for-each>
									<xsl:for-each select="ns0:ServiceDefinitionAssociation">
										<xsl:copy-of select="."/>
									</xsl:for-each>
									<xsl:for-each select="ns0:ServiceDefinitionID">
										<ns0:ServiceDefinitionID>
											<xsl:value-of select="."/>
										</ns0:ServiceDefinitionID>
									</xsl:for-each>
								</ns0:ServiceDefinition>
							</xsl:for-each>
						</ns0:ServiceDefinitionList>
					</xsl:for-each>
				</ns0:DataLists>
				<ns0:Order>
					<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:Order/ns0:OrderID">
						<ns0:OrderID>
							<xsl:value-of select="."/>
						</ns0:OrderID>
					</xsl:for-each>
					<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:Order/ns0:OwnerCode">
						<ns0:OwnerCode>
							<xsl:value-of select="."/>
						</ns0:OwnerCode>
					</xsl:for-each>
					<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:Order/ns0:StatusCode">
						<ns0:StatusCode>
							<xsl:value-of select="."/>
						</ns0:StatusCode>
					</xsl:for-each>
					<xsl:for-each select="ns4:IATA_OrderViewRS/ns4:Response/ns0:Order/ns0:OrderItem">
						<ns0:OrderItem>
							<xsl:for-each select="ns0:FareDetail">
								<ns0:FareDetail>
									<xsl:for-each select="ns0:FareComponent">
										<xsl:for-each select="ns0:PaxSegmentRefID">
											<ns0:FareComponent>
												<xsl:copy-of select="../ns0:CancelRestrictions"/>
												<xsl:copy-of select="../ns0:ChangeRestrictions"/>
												<xsl:for-each select="../ns0:FareBasisCityPairText">
													<ns0:FareBasisCityPairText>
														<xsl:value-of select="."/>
													</ns0:FareBasisCityPairText>
												</xsl:for-each>
												<xsl:for-each select="../ns0:FareBasisCode">
													<ns0:FareBasisCode>
														<xsl:value-of select="."/>
													</ns0:FareBasisCode>
												</xsl:for-each>
												<xsl:copy-of select="../ns0:FareRule"/>
												<xsl:for-each select="../ns0:NegotiatedCode">
													<ns0:NegotiatedCode>
														<xsl:value-of select="."/>
													</ns0:NegotiatedCode>
												</xsl:for-each>
												<ns0:PaxSegmentRefID>
													<xsl:value-of select="."/>
												</ns0:PaxSegmentRefID>
												<xsl:for-each select="../ns0:Price">
													<ns0:Price>
														<xsl:for-each select="ns0:BaseAmount">
															<ns0:BaseAmount>
																<xsl:value-of select="."/>
															</ns0:BaseAmount>
														</xsl:for-each>
														<xsl:for-each select="ns0:TaxSummary">
															<ns0:TaxSummary>
																<xsl:for-each select="ns0:Tax">
																	<xsl:copy-of select="."/>
																</xsl:for-each>
																<xsl:for-each select="ns0:TotalTaxAmount">
																	<ns0:TotalTaxAmount>
																		<xsl:value-of select="."/>
																	</ns0:TotalTaxAmount>
																</xsl:for-each>
															</ns0:TaxSummary>
														</xsl:for-each>
													</ns0:Price>
												</xsl:for-each>
												<xsl:for-each select="../ns0:PriceClassRefID">
													<ns0:PriceClassRefID>
														<xsl:value-of select="."/>
													</ns0:PriceClassRefID>
												</xsl:for-each>
												<xsl:for-each select="../ns0:TicketDesigCode">
													<ns0:TicketDesigCode>
														<xsl:value-of select="."/>
													</ns0:TicketDesigCode>
												</xsl:for-each>
											</ns0:FareComponent>
										</xsl:for-each>
									</xsl:for-each>
									<xsl:for-each select="ns0:PaxRefID">
										<ns0:PaxRefID>
											<xsl:value-of select="."/>
										</ns0:PaxRefID>
									</xsl:for-each>
									<xsl:for-each select="ns0:Price">
										<ns0:Price>
											<xsl:copy-of select="ns0:TaxSummary"/>
										</ns0:Price>
									</xsl:for-each>
								</ns0:FareDetail>
							</xsl:for-each>
							<xsl:for-each select="ns0:OrderItemID">
								<ns0:OrderItemID>
									<xsl:value-of select="."/>
								</ns0:OrderItemID>
							</xsl:for-each>
							<xsl:for-each select="ns0:OwnerCode">
								<ns0:OwnerCode>
									<xsl:value-of select="."/>
								</ns0:OwnerCode>
							</xsl:for-each>
							<xsl:for-each select="ns0:PaymentTimeLimitDateTime">
								<ns0:PaymentTimeLimitDateTime>
									<xsl:value-of select="."/>
								</ns0:PaymentTimeLimitDateTime>
							</xsl:for-each>
							<xsl:for-each select="ns0:StatusCode">
								<ns0:StatusCode>
									<xsl:value-of select="."/>
								</ns0:StatusCode>
							</xsl:for-each>
							<xsl:for-each select="ns0:Price">
								<ns0:Price>
									<xsl:for-each select="ns0:BaseAmount">
										<ns0:BaseAmount>
											<xsl:value-of select="."/>
										</ns0:BaseAmount>
									</xsl:for-each>
									<xsl:copy-of select="ns0:TaxSummary"/>
									<xsl:for-each select="ns0:TotalAmount">
										<ns0:TotalAmount>
											<xsl:value-of select="."/>
										</ns0:TotalAmount>
									</xsl:for-each>
								</ns0:Price>
							</xsl:for-each>
							<xsl:for-each select="ns0:Service">
								<ns0:Service>
									<xsl:for-each select="ns0:BookingRef">
										<ns0:BookingRef>
											<xsl:for-each select="ns0:BookingEntity">
												<xsl:copy-of select="."/>
											</xsl:for-each>
											<xsl:for-each select="ns0:BookingID">
												<ns0:BookingID>
													<xsl:value-of select="."/>
												</ns0:BookingID>
											</xsl:for-each>
										</ns0:BookingRef>
									</xsl:for-each>
									<xsl:for-each select="ns0:OrderServiceAssociation">
										<ns0:OrderServiceAssociation>
											<xsl:copy-of select="ns0:PaxSegmentRef"/>
										</ns0:OrderServiceAssociation>
									</xsl:for-each>
									<xsl:for-each select="ns0:PaxRefID">
										<ns0:PaxRefID>
											<xsl:value-of select="."/>
										</ns0:PaxRefID>
									</xsl:for-each>
									<xsl:for-each select="ns0:ServiceID">
										<ns0:ServiceID>
											<xsl:value-of select="."/>
										</ns0:ServiceID>
									</xsl:for-each>
									<xsl:for-each select="ns0:StatusCode">
										<ns0:StatusCode>
											<xsl:value-of select="."/>
										</ns0:StatusCode>
									</xsl:for-each>
								</ns0:Service>
							</xsl:for-each>
						</ns0:OrderItem>
					</xsl:for-each>
					<xsl:copy-of select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:Order/ns0:TotalPrice"/>
				</ns0:Order>
				<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:Response/ns0:TicketDocInfo">
					<xsl:copy-of select="."/>
				</xsl:for-each>
			</ns4:Response>
			<ns4:PaymentFunctions>
				<xsl:copy-of select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:OrderAssociation"/>
				<ns0:PaymentProcessingSummary>
					<ns0:Amount>
						<xsl:attribute name="CurCode">
							<xsl:value-of select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:Amount/@CurCode"/>
						</xsl:attribute>
						<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:Amount">
							<xsl:value-of select="."/>
						</xsl:for-each>
					</ns0:Amount>
					<ns0:PaymentID>
						<xsl:value-of select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentID"/>
					</ns0:PaymentID>
					<ns0:PaymentProcessingSummaryPaymentMethod>
						<ns0:SettlementPlan>
							<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:OfflinePayment/ns0:PaymentTypeCode">
								<ns0:PaymentTypeCode>
									<xsl:value-of select="."/>
								</ns0:PaymentTypeCode>
							</xsl:for-each>
							<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:CardBrandCode">
								<ns0:PaymentTypeCode>CC</ns0:PaymentTypeCode>
							</xsl:for-each>
						</ns0:SettlementPlan>
						<ns0:PaymentCard>
							<ns0:CardBrandCode>
								<xsl:value-of select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:CardBrandCode"/>
							</ns0:CardBrandCode>
							<ns0:CardHolderName>
								<xsl:value-of select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:CardHolderName"/>
							</ns0:CardHolderName>
							<xsl:for-each select="ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:ExpirationDate">
								<ns0:ExpirationDate>
									<xsl:value-of select="."/>
								</ns0:ExpirationDate>
							</xsl:for-each>
							<ns0:MaskedCardID>
								<xsl:value-of select="ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:MaskedCardID"/>
							</ns0:MaskedCardID>
							<ns0:CardholderAddress>
								<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:CardholderAddress/ns0:CountryCode">
									<ns0:CountryCode>
										<xsl:value-of select="."/>
									</ns0:CountryCode>
								</xsl:for-each>
								<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:CardholderAddress/ns0:CountrySubDivisionName">
									<ns0:CountrySubDivisionName>
										<xsl:value-of select="."/>
									</ns0:CountrySubDivisionName>
								</xsl:for-each>
								<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:CardholderAddress/ns0:PostalCode">
									<ns0:PostalCode>
										<xsl:value-of select="."/>
									</ns0:PostalCode>
								</xsl:for-each>
								<xsl:for-each select="/ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard/ns0:CardholderAddress/ns0:StreetText">
									<ns0:StreetText>
										<xsl:value-of select="."/>
									</ns0:StreetText>
								</xsl:for-each>
							</ns0:CardholderAddress>
						</ns0:PaymentCard>
					</ns0:PaymentProcessingSummaryPaymentMethod>
					<ns0:PaymentStatusCode>
						<xsl:value-of select="ns4:IATA_OrderViewRS/ns4:PaymentFunctions/ns0:PaymentProcessingSummary/ns0:PaymentStatusCode"/>
					</ns0:PaymentStatusCode>
				</ns0:PaymentProcessingSummary>
			</ns4:PaymentFunctions>
		</ns4:IATA_OrderViewRS>
	</xsl:template>
</xsl:stylesheet>
