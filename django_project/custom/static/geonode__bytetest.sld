<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" xmlns:sld="http://www.opengis.net/sld">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>MCD12Q1 - type 1</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Opacity>0.85</sld:Opacity>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry quantity="1" color="#05450a" label="Evergreen Needleleaf Forests "/>
              <sld:ColorMapEntry quantity="2" color="#086a10" label="Evergreen Broadleaf Forests"/>
              <sld:ColorMapEntry quantity="3" color="#54a708" label="Deciduous Needleleaf Forests "/>
              <sld:ColorMapEntry quantity="4" color="#78d203" label="Deciduous Broadleaf Forests "/>
              <sld:ColorMapEntry quantity="5" color="#009900" label="Mixed Forests"/>
              <sld:ColorMapEntry quantity="6" color="#c6b044" label="Closed Shrublands"/>
              <sld:ColorMapEntry quantity="7" color="#dcd159" label="Open Shrublands"/>
              <sld:ColorMapEntry quantity="8" color="#dade48" label="Woody Savannas "/>
              <sld:ColorMapEntry quantity="9" color="#fbff13" label="Savannas"/>
              <sld:ColorMapEntry quantity="10" color="#b6ff05" label="Grasslands"/>
              <sld:ColorMapEntry quantity="11" color="#27ff87" label="Permanent Wetlands"/>
              <sld:ColorMapEntry quantity="12" color="#c24f44" label="Croplands"/>
              <sld:ColorMapEntry quantity="13" color="#a5a5a5" label="Urban and Built-up Lands"/>
              <sld:ColorMapEntry quantity="14" color="#ff6d4c" label="Cropland/Natural Vegetation Mosaics&#xd;"/>
              <sld:ColorMapEntry quantity="15" color="#69fff8" label="Permanent Snow and Ice "/>
              <sld:ColorMapEntry quantity="16" color="#f9ffa4" label="Barren"/>
              <sld:ColorMapEntry quantity="17" color="#1c0dff" label="Water Bodies"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>