importScripts('https://www.gstatic.com/firebasejs/7.10.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.10.0/firebase-messaging.js');
console.log('firebase called')
debugger
// Initialize the Firebase app in the service worker by passing in the
// messagingSenderId.
firebase.initializeApp({
    'apiKey': "apiKey",
    'authDomain': "authDomain",
    'databaseURL': "databaseURL",
    'projectId': "projectId",
    'storageBucket': "storageBucket",
    'messagingSenderId': "dfsdf",
    'appId': "appId",
    'measurementId': "measurementId"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
console.log(messaging)
console.log('hello')

messaging.onMessage((payload) => {
console.log('Message recieved ', payload);
});
//messaging.setBackgroundMessageHandler(function(payload) {
//console.log('inside fn')
//  console.log('[firebase-messaging-sw.js] Received background message ', payload);
//  // Customize notification here
//  console.log(JSON.parse(payload))
//  const data = JSON.parse(payload.data.notification)
//
//  const notificationTitle = data.title;
//  const notificationOptions = {
//    body: data.body
//  };
//
//  return self.registration.showNotification(notificationTitle,
//    notificationOptions);
//});
console.log('after firebase')
