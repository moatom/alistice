<template>
  <v-btn icon @click="dialog = true">
    <v-icon>mdi-account-cog</v-icon>
    <v-dialog v-model="dialog" width="600px" v-if="dialog">
      <v-card min-width="320px">
        <v-card-title>
          <span class="headline">Settings</span>
        </v-card-title>
        <v-tabs v-model="active_tab" background-color="white" grow height="40">
          <v-tab>basic</v-tab>
          <v-tab>other</v-tab>
        </v-tabs>
        <v-divider />
        <v-tabs-items v-model="active_tab">
          <tab1 :name="name" :iconUrl="iconUrl" @hide-dialog="dialog = false" />
          <tab2 @hide-dialog="dialog = false" />
        </v-tabs-items>
      </v-card>
    </v-dialog>
  </v-btn>
</template>

<script>
import Tab1 from "@/components/edit_dialog/Tab1";
import Tab2 from "@/components/edit_dialog/Tab2";

export default {
  props: {
    name: { type: String, required: true },
    iconUrl: { type: String, required: true }
  },
  components: { Tab1, Tab2 },
  data() {
    return {
      active_tab: 0,
      dialog: false
    };
  }
};
</script>

<style>
#clickable {
  text-decoration: none;
  color: black;
}

.croppie-btn {
  border-radius: 8px;
  padding: 6px;
  background-color: #d3d3d3;
  font-weight: bold;
  cursor: pointer;
  margin: auto 1px;
}
</style>
