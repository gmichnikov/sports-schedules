function triggerFunction(e) {
    // Check if the edit is on the "doltin" sheet
    var sheet = e.range.getSheet();
    if (sheet.getName() !== "doltin") {
      return; // Exit if the edit is not on the "doltin" sheet
    }
  
    // Check if B1 is checked
    var b1Value = sheet.getRange("B1").getValue();
    if (b1Value) {
      getDoltEvents(); // Call your function if B1 is checked
    }
  }
  
  function getDoltEvents() {
    // var url = "https://www.dolthub.com/api/v1alpha1/gmichnikov/sports-schedules/main?q=SELECT+league%2C+%60date%60%2C+day%2C+%60time%60%2C+home_team%2C+road_team%2C+location+%0AFROM+%60combined-schedule%60%0AWHERE+home_state+IN+%28%22NY%22%2C+%22NJ%22%29%0AAND+%60date%60+%3E%3D+CURDATE%28%29+AND+%60date%60+%3C%3D+DATE_ADD%28CURDATE%28%29%2C+INTERVAL+7+DAY%29%0AORDER+BY+%60date%60%2C+%60time%60+ASC%0A";
  
    var selectClause = "SELECT league, `date`, SUBSTRING(day, 1, 3) as day, `time`, home_team, road_team, location "
    var fromClause = "FROM `combined-schedule` " 
    // var whereClause = "WHERE home_state IN (\"MA\", \"CT\") AND `date` >= CURDATE() AND `date` <= DATE_ADD(CURDATE(), INTERVAL 10 DAY) " 
    var whereClause = buildDynamicWhereClause();
    var orderClause = "ORDER BY `date`, `time` ASC"
    Logger.log(whereClause);
  
    var sqlQuery = selectClause + fromClause + whereClause + orderClause;
  
    var encodedQuery = encodeURIComponent(sqlQuery);
    var baseUrl = "https://www.dolthub.com/api/v1alpha1/gmichnikov/sports-schedules/main?q="
  
    var response = UrlFetchApp.fetch(baseUrl + encodedQuery);
    var json = response.getContentText();
    var data = JSON.parse(json);
    var rows = data["rows"];
  
    var doltoutSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("doltout")
    Logger.log(rows)
  
    if (rows.length === 0) return; // Check if rows is empty
  
    // Extract headers
    // var headers = Object.keys(rows[0]);
  
    // Define headers explicitly in the desired order
    var headers = ["day", "date", "home_team", "road_team", "location", "time", "league"];
  
    // Prepare data array
    var data = rows.map(row => headers.map(header => row[header] || ''));
  
    // Clear existing data
    doltoutSheet.clear();
  
    // Set headers
    doltoutSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
    // Set data
    if (data.length > 0) {
      doltoutSheet.getRange(2, 1, data.length, headers.length).setValues(data);
    }
  
    var lastColumn = doltoutSheet.getLastColumn();
    doltoutSheet.autoResizeColumns(1, lastColumn);
    doltoutSheet.setColumnWidth(1, 40);
    doltoutSheet.setColumnWidth(3, 100);
    doltoutSheet.setColumnWidth(4, 100);
    doltoutSheet.setColumnWidth(5, 150);
  
    var currentFilter = doltoutSheet.getFilter();
    if (currentFilter) {
      currentFilter.remove();
    }
    var range = doltoutSheet.getDataRange();
    // 1. Apply a filter over the range
    range.createFilter();
    // 2. Freeze the top row
    doltoutSheet.setFrozenRows(1);
    doltoutSheet.setFrozenColumns(2);
    // 3. Bold the top row
    var firstRowRange = doltoutSheet.getRange(1, 1, 1, doltoutSheet.getLastColumn());
    firstRowRange.setFontWeight('bold');
  
    // 4. Set alternating colors on the range
    var existingBanding = range.getBanding();
    if (existingBanding) {
      existingBanding.remove();
    }
  
    var banding = range.applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY);
    // banding.setHeaderRowColor('#ffffff'); // Set header row color if needed
  
    SpreadsheetApp.getActiveSpreadsheet().setActiveSheet(doltoutSheet);
  }
  
  function buildDynamicWhereClause() {
    var doltinSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("doltin");
    var range = doltinSheet.getRange("B2:D6");
    var values = range.getValues();
  
    var whereParts = [];
  
    // Date range filter
    if (values[0][0] === true) { // If B2 is checked
      var startDate = formatDate(values[0][1]);
      var endDate = formatDate(values[0][2]);
      whereParts.push("`date` >= DATE(\"" + startDate + "\") AND `date` <= DATE(\"" + endDate + "\")");
    }
  
    // Filter for next X days
    if (values[1][0] === true) { // If B3 is checked
      var intervalDays = values[1][1];
      whereParts.push("`date` >= CURDATE() AND `date` <= DATE_ADD(CURDATE(), INTERVAL " + intervalDays + " DAY)");
    }
  
    // State filter
    if (values[2][0] === true) { // If B4 is checked
      // var states = [values[2][1], values[2][2], values[2][3]].filter(Boolean).map(state => "\"" + state + "\"");
      var states = [values[2][1], values[2][2]].filter(Boolean).map(state => "\"" + state + "\"");
      if (states.length > 0) {
        whereParts.push("home_state IN (" + states.join(", ") + ")");
      }
    }
  
    // Sport filter
    if (values[3][0] === true) { // If B5 is checked
      var sport = values[3][1];
      if (sport != "") {
        whereParts.push("sport = \"" + sport + "\"");
      }
    }
  
    // League filter
    if (values[4][0] === true) { // If B6 is checked
      var league = values[4][1];
      if (league != "") {
        whereParts.push("league = \"" + league + "\"");
      }
    }
  
    var whereClause = whereParts.length > 0 ? "WHERE " + whereParts.join(" AND ") : "";
    return whereClause;
  }
  
  function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();
  
    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;
  
    return [year, month, day].join('-');
  }
  