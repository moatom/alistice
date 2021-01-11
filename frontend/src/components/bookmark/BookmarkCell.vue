<template>
  <li @click="$emit('click', $event)">
    <div class="body-part">
      <div class="input-part">
        <input type="checkbox" :checked="check" />
      </div>
      <slot />
    </div>
    <div class="select-part">
      <v-menu top :offset-y="true">
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on"><v-icon>mdi-dots-vertical</v-icon></v-btn>
        </template>

        <v-list>
          <v-list-item
            v-for="(item, index) in items"
            :key="index"
            @click.stop="fns[index]"
          >
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
  </li>
</template>

<script>
export default {
  props: {
    username: String,
    val: Object,
    check: Boolean
  },
  data() {
    return {
      // editing: false,
      items: [
        { title: "Edit" },
        { title: "Select up to here" },
        { title: "Open all" }
      ],
      fns: [
        this.edit,
        this.select_up_to_here,
        this.open_all
      ]
    };
  },
  methods: {
    edit() {
      // this.$store.dispatch("editBookmark", this.username);
    },
    select_up_to_here() {
      const evt = new MouseEvent("click", {
        shiftKey: true
      });
      this.$emit("click", evt);
    },
    open_all() {
      this.$store.dispatch("openBookmarks", this.username);
    },
    merge() {}
  }
};
</script>

<style scoped>
li {
  height: 50px;
  line-height: 50px;
}

.body-part {
  float: left;
  width: 93%;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.input-part {
  display: inline-block;
  width: 10%;
  padding-left: 4%;
}

.icon-part {
  vertical-align: middle;
}

a {
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.icon-part {
  height: 16px;
  width: 16px;
  vertical-align: middle;
}

.select-part {
  max-width: 7%;
  float: right;
}
</style>
