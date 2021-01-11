<template>
  <v-card flat class="pa-3">
    <h1>Profile</h1>
    <v-divider></v-divider>
    <br />
    <div v-if="name">
      <!-- 73*73 to 39*39 -->
      <img
        :src="userIcon"
        class="mr-2"
        style="height: 60px; width: 60px; float: left; vertical-align: middle;"
      />
      <h3>{{ name }}</h3>
      {{ username }}
      <!-- Because each component is reused, we need v-if to ensure the newness of it's creation. -->
      <edit-dialog
        :name="name"
        :iconUrl="userIcon"
        v-if="$store.state.username === username"
      />
    </div>
    <br />
    <br />
    <v-tabs v-model="active_tab" background-color="white" grow height="40">
      <v-tab
        v-for="tab in tabs"
        :key="tab.id"
        @change="$router.push(tab.route).catch(() => {})"
      >
        {{ tab.name }}
      </v-tab>
    </v-tabs>
    <v-divider></v-divider>
    <div id="profile">
      <router-view />
    </div>
  </v-card>
</template>

<script>
import { UserApi, StaticApi } from "@/common/api";
import EditDialog from "@/components/edit_dialog/EditDialog";

export default {
  props: {
    username: String
  },
  components: {
    EditDialog
  },
  data: function() {
    return {
      active_tab: 0,
      root_id: 0,
      name: null,
      tabs: [
        {
          id: 0,
          name: "recents",
          route: {
            name: "recents"
          }
        },
        {
          id: 1,
          name: "tree",
          route: {
            name: "tree",
            params: { username: this.username, bm_id: "" }
          }
        }
      ]
    };
  },
  computed: {
    userIcon() {
      return `${StaticApi.USERICON_URL}/${this.username}.png`;
    }
  },
  methods: {
    initData() {
      this.tabs[1].route.params.bm_id = this.root_id.toString();
    },
    syncTab() {
      if (
        this.$route.path === `/${this.username}/` ||
        this.$route.path === `/${this.username}`
      ) {
        this.active_tab = 0;
      } else {
        this.active_tab = 1;
      }
    }
  },
  created: function() {
    UserApi.get(this.username).then(({ data }) => {
      // @fix root_id is already owned by sidecard in store. however separating them is also good.
      this.root_id = data.root_id;
      this.name = data.name;
      this.initData();
    });
  },
  updated: function() {
    this.syncTab();
  }
};
</script>
