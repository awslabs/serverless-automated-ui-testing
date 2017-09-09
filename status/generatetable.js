/*jshint esversion: 6 */

AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'Cognito_IDP_ID',
});
AWS.config.region = "AWS_REGION";
var ddb = new AWS.DynamoDB.DocumentClient();
var body, chrome_tab, firefox_tab;
var firstload = 1;

function getdata(modlist, params, brw){
  var flag;
  var tbl = document.createElement('table');
  if (brw == 'Chrome'){
    tbl.setAttribute('id', 'Chrome_table');
  }
  if (brw == 'Firefox'){
    tbl.setAttribute('id', 'Firefox_table');
  }
  if (brw == 'PhantomJS'){
    tbl.setAttribute('id', 'PhantomJS_table');
  }
  thead = tbl.createTHead();
  tr = thead.insertRow();
  td = tr.insertCell();
  td.appendChild(document.createTextNode(brw));
  td.style.fontSize = 'x-large';
  td.style.fontWeight = 'bolder';
  td.setAttribute('colSpan', '7');
  tr = thead.insertRow();
  tr.style.fontSize = 'large';
  tr.style.fontWeight = 'bolder';
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Module'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Testcase'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Status'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Start Time'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('End Time'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Time Taken (ms)'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Error Message'));
  ddb.scan(params, function (err, data) {
    if (err) console.error(err, err.stack); // an error occurred
    else {
      tdata = data.Items;
      console.log(tdata);
      for (var mod in modlist){
        var newmod = 1;
        for (var tc in modlist[mod]){
          if (newmod == 1){
            tr = tbl.insertRow();
            td = tr.insertCell();
            td.appendChild(document.createTextNode(mod));
            td.setAttribute('rowSpan', modlist[mod].length+1);
            newmod = 0;
          }
          flag = 1;
          for (i=0; i< tdata.length; i++){
            tcdetails = tdata[i].testcaseid.split('-');
            if (tdata[i].module == mod && tcdetails[0] == brw.toLowerCase() && tcdetails[1] == modlist[mod][tc]){
              tr = tbl.insertRow();
              td = tr.insertCell();
              td.appendChild(document.createTextNode(modlist[mod][tc]));
              td = tr.insertCell();
              td.appendChild(document.createTextNode(tdata[i].details.Status));
              if ( tdata[i].details.Status == 'Passed' ){
                td.style.color = 'green';
              }
              else {
                td.style.color = 'red';
              }
              td = tr.insertCell();
              td.appendChild(document.createTextNode(tdata[i].details.StartTime));
              td = tr.insertCell();
              td.appendChild(document.createTextNode(tdata[i].details.EndTime));
              td = tr.insertCell();
              td.appendChild(document.createTextNode(tdata[i].details.TimeTaken));
              td = tr.insertCell();
              td.appendChild(document.createTextNode(tdata[i].details.ErrorMessage));
              flag = 0;
            }
          }
          if (flag == 1){
            tr = tbl.insertRow();
            td = tr.insertCell();
            td.appendChild(document.createTextNode(modlist[mod][tc]));
            td = tr.insertCell();
            td.appendChild(document.createTextNode(' '));
            td = tr.insertCell();
            td.appendChild(document.createTextNode(' '));
            td = tr.insertCell();
            td.appendChild(document.createTextNode(' '));
            td = tr.insertCell();
            td.appendChild(document.createTextNode(' '));
            td = tr.insertCell();
            td.appendChild(document.createTextNode(' '));
          }
        }
      }
    }
  });
  return tbl;
}


function tableCreate() {
  var modparams = {
    TableName: 'Modules_Table',
  };
  var modlist = {};
  console.log(modparams);
  ddb.scan(modparams, function (err, data) {
    if (err) console.error(err, err.stack);
    else {
      var mdata = data.Items;
      for (var m in mdata){
        modlist[mdata[m].module] = mdata[m].testcases;
      }
    }
  });
  var browsers = ['Chrome', 'Firefox', 'PhantomJS'];
  var br;
  var tbl;
  var params;
  for (br in browsers){
    params = {
      TableName: 'Status_Table',
      FilterExpression: "begins_with(testcaseid, :tcid)",
      ExpressionAttributeValues: {
       ":tcid": browsers[br].toLowerCase()
      }
    };
    if (browsers[br] == 'Chrome'){
      ch_tbl = getdata(modlist, params, 'Chrome');
    }
    if (browsers[br] == 'Firefox'){
      ff_tbl = getdata(modlist, params, 'Firefox');
    }
    if (browsers[br] == 'PhantomJS'){
      pjs_tbl = getdata(modlist, params, 'PhantomJS');
    }
  }
  body.replaceChild(ff_tbl, document.getElementById('Firefox_table'));
  body.replaceChild(ch_tbl, document.getElementById('Chrome_table'));
  body.replaceChild(pjs_tbl, document.getElementById('PhantomJS_table'));
}

document.addEventListener("DOMContentLoaded", function(event) {
  body = document.body;
  if (firstload == 1){
    chrome_tab  = document.createElement('table');
    firefox_tab  = document.createElement('table');
    phantomjs_tab = document.createElement('table');
    chrome_tab.setAttribute('id', 'Chrome_table');
    firefox_tab.setAttribute('id', 'Firefox_table');
    phantomjs_tab.setAttribute('id', 'PhantomJS_table');
    body.appendChild(chrome_tab);
    body.appendChild(document.createElement('br'));
    body.appendChild(firefox_tab);
    body.appendChild(document.createElement('br'));
    body.appendChild(phantomjs_tab);
    tableCreate();
    firstload = 0;
  }
});
