//Add a link to your data object, and use v-bind to sync it up with an anchor tag in your HTML. Hint: you’ll be binding to the href attribute.

var app = new Vue({
  el: '#app',
  data: {
    jwt: "",
    username: "",
    password: ""
  }, 
  computed: {
    // this.jwtData will update whenever this.jwt changes.
    jwtData() {
      // JWT's are two base64-encoded JSON objects and a trailing signature
      // joined by periods. The middle section is the data payload.
      if (this.jwt) return {
         identity: JSON.parse(atob(this.jwt['access_token'].split('.')[1])).identity,
         access_token:this.jwt['access_token'],
         refresh_token:this.jwt['refresh_token'],
         };
      return {};
    }
  },
  methods: {
    async login() {
      // Error handling and such omitted here for simplicity.
      const res = await fetch(`/auth`,{
        method: 'POST',
        headers: new Headers({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify({"username": this.username, "password" : this.password})
      });
      this.jwt = await res.json();
    },

    async fetchJWT() {
      // Error handling and such omitted here for simplicity.
      const res = await fetch(`/auth`,{
        method: 'POST',
        headers: new Headers({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify({"username": "fabrizio2", "password" : "pwd2"})
      });
      this.jwt = await res.json();
    },

    async doSomethingWithJWT() {
      const res = await fetch(`http://localhost/vuejs-jwt-example/do-something`, {
        method: 'POST',
        headers: new Headers({
          'Authorization': `Bearer: ${this.jwt}`
        })
      });
      // Do stuff with res here.
    }
  },
  mounted() {
    this.fetchJWT();
  }
})


