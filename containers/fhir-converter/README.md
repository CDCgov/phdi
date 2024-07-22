# FHIR Converter
## Testing
When testing, you can print from the liquid templates with the following command in the templates.
```
{{ "string" | print_object }}
{{ objectName | print_object }}
```

This will print objects or strings to the console for debugging purposes.