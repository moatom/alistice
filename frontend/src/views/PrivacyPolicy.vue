<template>
  <v-card flat class="pa-3">
    <div id="privacy">
      <h1>Alistice Privacy Policy</h1>
      <v-divider></v-divider>
      <div class="pa-5">
        <h4>Written in Japanese</h4>
        <br />{{ privacy }}
      </div>
    </div>
  </v-card>
</template>

<script>
import privacy from "@/assets/privacy";

export default {
  name: "privacy",
  components: {},
  data: () => ({ privacy: privacy })
};
</script>

<style scoped>
#privacy {
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  text-indent: 0px !important;
}

#privacy::before {
  content: none !important;
}
</style>
