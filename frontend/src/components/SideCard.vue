<template>
  <v-card flat width="135">
    <v-card-text id="side-card">
      <div v-if="login" class="loggin-btns">
        <!-- <v-btn :to="'/user/' + $store.state.username" text outlined class="ma-1">
          <span>profile</span>
        </v-btn> -->
        <v-btn :to="{
                      name: 'recents',
                      params: { username: $store.state.username }
                    }" text outlined class="ma-1">
          <span>profile</span>
        </v-btn>
        <br />
        <v-btn to="/import" text outlined class="ma-1">
          <span>import</span>
        </v-btn>
        <br />
        <v-btn text outlined class="ma-1" @click="logout">
          <span>logout</span>
        </v-btn>
        <br />
      </div>
      <div v-else>
        <v-btn to="/login" text outlined class="ma-1">
          <span>login</span>
        </v-btn>
        <br />
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import { AuthApi } from "@/common/api";

export default {
  data: function() {
    return {
      login: false
    };
  },
  created() {
    AuthApi.signin()
      .then(({ data }) => {
        this.$store.commit("setLogin", {
          username: data.username,
          root_id: data.root_id
        });
        this.login = data.login;
      })
      .catch(() => {
        this.login = false;
      });
  },
  methods: {
    logout() {
      AuthApi.signout().then(() => {
        window.alert("successfully logged out");
        this.login = false;
      });
    }
  }
};
</script>
