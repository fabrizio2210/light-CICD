<template>
  <div class="login">
    <p>Username:</p>
    <input v-model="username" placeholder="fabrizio2" />
    <p>Password:</p>
    <input v-model="password" placeholder="pwd2" />
    <button v-on:click="login()">Login</button>
    <button v-on:click="logout()">Logout</button>
    <p class="errorText" v-if="login_status == 2">{{ login_error }}</p>
    <a v-if="login_status == 1" href="/web/projects">Your projects</a>
  </div>
</template>

<script>
export default {
  name: "Login",
  data: function() {
    return {
      username: "fabrizio2",
      password: "pwd2",
      login_status: 0,
      login_error: ""
    };
  },
  methods: {
    async login() {
      // Error handling and such omitted here for simplicity.
      const res = await fetch(`http://192.168.121.19:5000/auth`,{
        method: "POST",
        headers: new Headers({
          "Content-Type": "application/json"
        }),
        body: JSON.stringify({"username": this.username, "password" : this.password})
      }).catch(error => {
        console.error('Proble during login:', error);
      });
      if (res.ok){
        var jwt = await res.json();
        this.$emit('setIdentity', JSON.parse(atob(jwt['access_token'].split('.')[1])).identity);
        this.$emit('setAccessToken', await jwt['access_token']);
        this.$emit('setRefreshToken', jwt['refresh_token']);
        this.login_status = 1;
        this.login_error = 1;
      } else {
        this.login_status = 2;
        this.login_error = (await res.json())['message'];
      }
    },

    logout: function() {
      this.$emit('setAccessToken', "");
      this.$emit('setRefreshToken', ""); 
    },
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
