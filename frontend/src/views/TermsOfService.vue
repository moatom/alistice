<template>
  <v-card flat class="pa-3">
    <div id="tos">
      <h1>Alistice Terms of Service</h1>
      <v-divider></v-divider>
      <div class="pa-5">
        <h4>Written in Japanese</h4>
        <br />{{ tos }}
      </div>
    </div>
  </v-card>
</template>

<script>
import tos from "@/assets/tos";

export default {
  name: "tos",
  components: {},
  data: () => ({ tos: tos })
};
</script>

<style scoped>
#tos {
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  text-indent: 0px !important;
}

#tos::before {
  content: none !important;
}
</style>
