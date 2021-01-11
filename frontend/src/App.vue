<template>
  <v-app>
    <app-bar />
    <v-content id="main-background" class="main-content">
      <v-container>
        <v-row no-gutters>
          <v-col cols="3">
            <side-card />
          </v-col>
          <v-col cols="8" class="ml-4">
            <router-view />
          </v-col>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import AppBar from "@/components/AppBar";
import SideCard from "@/components/SideCard";

export default {
  name: "App",
  components: {
    AppBar,
    SideCard
  }
};
</script>

<style>
#app {
  min-width: 565px;
}

.center-text {
  text-align: center;
  padding: 7px;
}

#main-background {
  background: #fafafa;
}
</style>
