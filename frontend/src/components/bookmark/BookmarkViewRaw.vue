<template>
  <v-card flat class="pa-3" v-if="children.length > 0">
    <h1>{{ title }}</h1>
    <v-divider></v-divider>
    <div v-if="option">
      <small>
        <em>
          <template v-if="titles.length != 1">
            <template v-for="(val, i) in titles.slice(0, titles.length - 1)">
              /
              <router-link
                :to="{ name: 'tree', params: { bm_id: ids[i].toString() } }"
                :key="ids[i]"
              >
                {{ val }}
              </router-link>
            </template>
          </template>
          <template v-else>/</template>
        </em>
      </small>

      <v-menu top :offset-y="true" close-delay="1">
        <template v-slot:activator="{ on }">
          <v-btn text outlined small v-on="on" class="on_right mt-1">order</v-btn>
        </template>
        <v-card>
          <v-divider />
          <v-radio-group
            v-model="sort"
            :mandatory="false"
            class="px-2"
          >
            <v-radio
              v-for="(item, index) in sorts"
              :label="item"
              :value="index"
              :key="index"
            />
          </v-radio-group>
          <v-divider />
        </v-card>
      </v-menu>
    </div>
    <br v-else />

    <bookmark-list
      class="mt-5"
      :username="username"
      :children="children"
      :sort="sort"
    />
  </v-card>
</template>

<script>
import BookmarkList from "@/components/bookmark/BookmarkList";

export default {
  props: {
    username: String,
    ids: { type: Array, required: true },
    titles: { type: Array, required: true },
    children: Array,
    option: { type: Boolean, default: true }
  },
  data() {
    return {
      sort: -1,
      sorts: ["Name", "Date", "Reversed Date"]
      // domain?
    };
  },
  components: {
    BookmarkList
  },
  computed: {
    title: function() {
      return this.titles[this.titles.length - 1];
    }
  },
  updated() {
    this.updateTitle(this.title, this.username);
  }
};
</script>

<style scoped>
.on_right {
  float: right;
}
</style>
