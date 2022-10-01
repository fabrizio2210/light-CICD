<template>
  <div class="login">
    <h1>This is a login page</h1>
    <Login
      v-on:setIdentity="jwtData.identity = $event"
      v-on:setRefreshToken="refresh_token = $event"
      v-on:setAccessToken="access_token = $event"
    />
  </div>
</template>

<script>
// @ is an alias to /src
import Login from "@/components/Login.vue";

export default {
  name: "LoginPage",
  components: {
    Login
  }
};
</script>
