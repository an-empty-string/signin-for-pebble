/**
 * Welcome to Pebble.js!
 *
 * This is where you write your app.
 */

var UI = require('ui');
var ajax = require('ajax');
var waitCard;

function checkPendingRequests() {
  console.log("Querying server....");
  ajax({url: "https://psignin.ngrok.com/api/" + localStorage.auth_key + "/pending.json", type: "json"}, function(response) {
    waitCard.hide();
    var card;
    if(!response.pending.length) {
      console.log("No pending requests");
      card = new UI.Card({
        title: "No pending signin requests"
      });
      card.show();
      card.on('click', 'select', function() {
        card.hide();
        checkPendingRequests();
      });
    }
    else {
      console.log("Pending requests " + response.pending);
      card = new UI.Card({
        title: "Signin to " + response.pending[0].service,
        body: "Press up to accept or down to deny"
      });
      card.show();
      card.on('click', 'up', function() {
        ajax({url: "https://psignin.ngrok.com/api/" + localStorage.auth_key + "/accept/" + response.pending[0].id}, function() {
          card.hide();
        });
      });
      card.on('click', 'down', function() {
        ajax({url: "https://psignin.ngrok.com/api/" + localStorage.auth_key + "/accept/" + response.pending[0].id}, function() {
          card.hide();
        });
      });
    }
  });
}

if(!localStorage.auth_key) {
  console.log("No key!");
  ajax({url: "https://psignin.ngrok.com/api/new_key.json", type: "json"}, function(key_response) {
    console.log("Got key" + key_response.auth_key);
    var card = new UI.Card({
      title: "Please enroll this Pebble",
      body: "Use enrollment token " + key_response.enrollment_token + ". Press the center button once you have enrolled"
    });
    card.show();
    card.on('click', 'select', function() {
      localStorage.auth_key = key_response.auth_key;
      // card.hide();
      checkPendingRequests();
    });
  });
}

else {
  console.log(localStorage.auth_key + " is my key");
  waitCard = new UI.Card({title: "Waiting for server"});
  waitCard.show();
  ajax({url: "https://psignin.ngrok.com/api/" + localStorage.auth_key + "/ok.json", type: "json"}, function(data) {
    if(data.ok) {
      checkPendingRequests();
    } else {
      localStorage.auth_key = undefined;
      waitCard.hide();
    }
  });
  
}