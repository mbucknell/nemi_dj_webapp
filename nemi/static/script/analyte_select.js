function showAnalyteFind(url){
	//Determines which analyte kind has been selected. This defaults to "name" 
	var searchForm = document.getElementById('search-form');
	
	var analyteKindR = searchForm.elements["analyte_kind"]; 
	var kind = "name";
	for(var i=0; i < analyteKindR.length; i++){
		if (analyteKindR[i].checked){
			kind = analyteKindR[i].value;
			break;
		}
	}
	
	// Retrieve the value in the analyte_value text field  and create selection parameter for find analyte form. 
	var selection = searchForm.elements["analyte_value"].value;
	var selectionParam = "";
	if (selection != ""){
		selectionParam = "&selection=" + selection;
	}
	// Disable the search-form while the pop up dialog is up and then pop up it up. 
	$('#search-form input').attr("disabled", true);
	winPopup(url + "?kind=" + kind + selectionParam);
}
