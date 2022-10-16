# OVOS PHAL Color Scheme Plugin

The Dashboard PHAL plugin provides a middle layer interface between OVOS Shell and OVOS Core to set and manage color schemes. This interface is used for theme generaation feature and theme setting feature

# Requirements
- This plugin has not external requirements

# Install
`pip install ovos-PHAL-plugin-color-scheme-manager`

# Event Details:

##### Theme Setting and Theme Generation

``` python

 # type: Request
 # data requirements: "theme_name", "primaryColor", "secondaryColor", "textColor"
 # "ovos.shell.gui.color.scheme.generate"

```
