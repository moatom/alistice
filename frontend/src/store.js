import Vue from "vue";
import Vuex from "vuex";
import { AuthApi, BookmarkApi } from "@/common/api";
Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    move: new Set(),
    loading: false,
    login: false,
    // aggregate them to user?
    username: null,
    root_id: null
  },
  mutations: {
    // rename move to srcs. now, not id
    addMove(state, id) {
      state.move = new Set(state.move.add(id));
    },
    deleteMove(state, id) {
      state.move.delete(id);
      state.move = new Set(state.move);
    },
    clearMove(state) {
      state.move.clear();
      state.move = new Set(state.move);
    },
    setLogin(state, { username, root_id }) {
      state.login = true;
      state.username = username;
      state.root_id = root_id;
    },
    unsetLogin(state) {
      state.login = false;
      state.username = null;
      state.root_id = null;
    }
  },
  actions: {
    openBookmarks({ getters }, username) {
      getters.moveUrl(username).forEach(element => {
        window.open(element, "_blank");
      });
    },
    signin({ commit }, payload) {
      AuthApi.signin(payload).then(res => {
        commit("setLogin", {
          username: res.data.username,
          root_id: res.data.root_id
        });
        // @fix
        window.location.assign("/");
      });
    },
    // eslint-disable-next-line
    signup({ commit }, payload) {
      alert(
        "In order to complete your signup, \nyou need to read an email we sent now."
      );
      AuthApi.signup(payload).then(() => {
        // @fix @check 本当にホームへ遷移させるべき?
        Vue.$router.push("/");
        // window.location.assign("/");
      });
    },
    deleteBookmarks({ getters }) {
      return BookmarkApi.delete({ srcs: getters.moveId });
    },
    moveBookmarks({ getters }, payload) {
      return BookmarkApi.move({ srcs: getters.moveId, dest: payload });
    }
  },
  getters: {
    moveId(state) {
      return [...state.move].map(e => e.id);
    },
    moveUrl: state => username => {
      return [...state.move].map(e => {
        if (e.type === 0) {
          return `${process.env.VUE_APP_BASE_URL}/${username}/tree/${e.id}`;
        } else {
          return e.url;
        }
      });
    },
    login(state) {
      return state.login;
    }
  }
});

export default store;
