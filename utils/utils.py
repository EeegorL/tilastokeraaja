def locationCode(location: str): 
    match(location.upper()):
        case "KAISA":
            return "138";
        case "KUMPULA":
            return "134";
        case "TERKKO":
            return "136";
        case "VIIKKI":
            return "140";
        case _: pass;

def sheetColumn(location: str): 
    match(location.upper()):
        case "KAISA":
            return "B";
        case "KUMPULA":
            return "C";
        case "TERKKO":
            return "D";
        case "VIIKKI":
            return "E";
        case _: pass;