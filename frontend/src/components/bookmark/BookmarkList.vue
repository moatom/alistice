<template>
  <ul>
    <bookmark-cell
      :username="username"
      :val="val"
      :check="checks[i]"
      :key="val.id"
      @click.exact="toggleCheck(i, val)"
      @click.shift="shiftedToggleCheck(i)"
      v-for="(val, i) in folders"
    >
      <v-icon class="icon-part" small>mdi-folder-outline</v-icon>

      <router-link
        :to="{
          name: 'tree',
          params: { username: username, bm_id: val.id.toString() }
        }"
        @click.native.stop
      >
        <template v-if="val.title">
          {{ val.title }}
        </template>
        <template v-else>
          &lt;EMPTY&gt;
        </template>
      </router-link>
    </bookmark-cell>

    <bookmark-cell
      :username="username"
      :val="val"
      :check="checks[i + folders.length]"
      :key="val.id"
      @click.exact="toggleCheck(i + folders.length, val)"
      @click.shift="shiftedToggleCheck(i + folders.length)"
      v-for="(val, i) in bookmarks"
    >
      <img class="icon-part" :src="favAddr(val.url)" />
      <a :href="val.url" target="_blank" @click.stop>
        <template v-if="val.title">
          {{ val.title }}
        </template>
        <template v-else>
          &lt;EMPTY&gt;
        </template>
      </a>
    </bookmark-cell>
  </ul>
</template>

<script>
import BookmarkCell from "./BookmarkCell";
import { StaticApi } from "@/common/api";

export default {
  props: {
    username: String,
    children: Array,
    sort: Number
  },
  components: {
    BookmarkCell
  },
  data() {
    return {
      checks: Array(this.children.length).fill(false),
      last_selection_range: {
        start: null,
        end: null
      }
    };
  },
  watch: {
    $route() {
      this.checks = Array(this.children.length).fill(false);
    }
  },
  computed: {
    folders: function() {
      return this.children
        .filter(function(element) {
          return element.type === 0;
        })
        .sort(this.sorter);
    },
    bookmarks: function() {
      return this.children
        .filter(function(element) {
          return element.type === 1;
        })
        .sort(this.sorter);
    },
    sorted_children() {
      return Array.of(...this.folders, ...this.bookmarks);
    }
  },
  methods: {
    // https://goma.pw/article/2015-11-18-0/
    sorter_raw(a, b) {
      let mod_a = a.toString().toLowerCase();
      let mod_b = b.toString().toLowerCase();
      if (mod_a < mod_b) {
        return -1;
      } else if (mod_a > mod_b) {
        return 1;
      } else {
        return 0;
      }
    },
    sorter(a, b) {
      switch (this.sort) {
        case 0:
          return this.sorter_raw(a["title"], b["title"]);
        case 1:
          return this.sorter_raw(a["created_at"], b["created_at"]);
        case 2:
          return this.sorter_raw(b["created_at"], a["created_at"]);
        default:
          return 0;
      }
    },
    toDomain: function(url) {
      return url.split("/")[2];
    },
    favAddr: function(url) {
      return `${StaticApi.FAV_URL}/${this.toDomain(url)}.png`;
    },
    toggleCheck: function(i, val) {
      this.last_selection_range.start = i;
      this.last_selection_range.end = null;
      this.checks.splice(i, 1, !this.checks[i]);
      if (this.checks[i]) {
        this.$store.commit("addMove", val);
      } else {
        this.$store.commit("deleteMove", val);
      }
    },
    orded_call_f(f, s, e) {
      if (s <= e) {
        for (let i = s + 1; i <= e; i++) {
          f(i);
        }
      } else {
        for (let i = s - 1; i >= e; i--) {
          f(i);
        }
      }
    },
    shiftedToggleCheck: function(e) {
      if (this.last_selection_range.start !== null) {
        if (this.last_selection_range.end !== null) {
          this.orded_call_f(
            i => {
              this.checks.splice(i, 1, !this.checks[i]);
              this.$store.commit("deleteMove", this.sorted_children[i]);
            },
            this.last_selection_range.start,
            this.last_selection_range.end
          );
        }
        this.orded_call_f(
          i => {
            this.checks.splice(i, 1, !this.checks[i]);
            this.$store.commit("addMove", this.sorted_children[i]);
          },
          this.last_selection_range.start,
          e
        );
        this.last_selection_range.end = e;
      } else {
        this.toggleCheck(e, this.sorted_children[e]);
      }
    }
  }
};
</script>

<style scoped>
ul {
  list-style: none;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  padding-left: 0px !important;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

li {
  border-top: 1px solid rgba(0, 0, 0, 0);
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

li:last-child {
  border-bottom-width: 0px;
}
</style>
