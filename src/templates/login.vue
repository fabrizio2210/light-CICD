<div id="app">

  <div>
    <p>Username:</p>
    <input v-model="username" placeholder="fabrizio2">
    <p>Password:</p>
    <input v-model="password" placeholder="pwd2">
    <button v-on:click="login()">Login</button>
  </div>

  <div>
    <p>JWT: {{jwt}}</p>
    <p>User ID: {{jwtData.identity}}</p>
    <p>Access: {{jwtData.access_token}}</p>
    <p>Refresh: {{jwtData.refresh_token}}</p>
    <button v-on:click="doSomethingWithJWT()">Do Something</button>
  </div>

</div> 

<link rel="stylesheet" href="/css/stylesheet.css">
<script src="https://cdn.jsdelivr.net/npm/vue@2.5.13/dist/vue.js"></script>
<script src="/js/main.js"></script>
