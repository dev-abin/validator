

from slicer import extract_xslt_slice
from merge_fix import replace_xslt_slice


xslt_string = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes"/>

  <!-- SINGLE TEMPLATE -->
  <xsl:template match="/">

    <Invoice>

      <Header>
        <InvoiceNumber>
          <xsl:value-of select="/Order/OrderHeader/OrderID"/>
        </InvoiceNumber>

        <Buyer>
          <Name>
            <xsl:value-of select="/Order/Customer/Name"/>
          </Name>
          <!-- BUG: TaxID missing -->
        </Buyer>
      </Header>

      <Lines>
        <xsl:for-each select="/Order/Items/Item">
          <Line>
            <LineNumber>
              <xsl:value-of select="position()"/>
            </LineNumber>

            <ProductCode>
              <xsl:value-of select="Product/Code"/>
            </ProductCode>

            <Amount>
              <xsl:value-of select="Price * Quantity"/>
            </Amount>
          </Line>
        </xsl:for-each>
      </Lines>

      <Total>
        <xsl:variable name="sum">
          <xsl:value-of select="sum(/Order/Items/Item/Price)"/>
        </xsl:variable>
        <xsl:value-of select="$sum"/>
      </Total>

    </Invoice>

  </xsl:template>
</xsl:stylesheet>
"""
print(len(xslt_string))



def main():
    print("Hello from refiner!")
    
    diff = {
    "output_xpath": "/Invoice/Header/Buyer/TaxID",
    "status": "MISSING",
    "expected_rule": "TaxID must be copied from customer tax number",
    "expected_source_xpath": "/Order/Customer/TaxNumber"
    }
    
    xslt_slice = extract_xslt_slice(xslt_string, diff)
    print(len(xslt_slice))
    print(xslt_slice)

    # Step 2: Send to LLM → get fixed_slice_xml
    fixed_slice_xml = """<Buyer>
    <Name>
        <xsl:value-of select="/Order/Customer/Name"/>
    </Name>
    <TaxID>
        <xsl:value-of select="/Order/Customer/TaxNumber"/>
    </TaxID>
    </Buyer>
    """

    # Step 3: Replace into full XSLT
    updated_xslt = replace_xslt_slice(
        xslt_string,
        diff["output_xpath"],
        fixed_slice_xml
    )

    print(updated_xslt)

    



if __name__ == "__main__":
    main()
