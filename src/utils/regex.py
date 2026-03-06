import re

numeric_re = r'\d+|(\d+(,\d{3})*(\.\d+)?)'
redacted_re = r'([Rr][Ee][Dd][Aa][Cc][Tt][Ee][Dd])'
na_re = r'([Nn]/{0,1}[Aa])|[Nn][Oo][Tt] [Aa][Pp][Pp][Ll][Ii][Cc][Aa][Bb][Ll][Ee]'
missing_field_re = '[Mm][Ii][Ss][Ss][Ii][Nn][Gg] [Ff][Ii][Ee][Ll][Dd]'
not_provided_re = r'[Nn][Oo][Tt] [Pp][Rr][Oo][Vv][Ii][Dd][Ee][Dd]'