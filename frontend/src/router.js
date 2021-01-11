import Vue from "vue";
import Router from "vue-router";
import store from "./store";
Vue.use(Router);

const router = new Router({
  mode: "history",
  base: process.env.BASE_URL,
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("./views/Home.vue")
      // component: () => import(/* webpackChunkName: "home" */ "./views/Home.vue")
    },
    {
      path: "/login",
      name: "login",
      component: () => import("./views/Login.vue")
    },
    {
      path: "/import",
      name: "import",
      component: () => import("./views/Import.vue")
    },
    {
      path: "/tos",
      name: "tos",
      component: () => import("./views/TermsOfService.vue")
    },
    {
      path: "/privacy",
      name: "privacy",
      component: () => import("./views/PrivacyPolicy.vue")
    },
    {
      path: "/search/:query",
      name: "search",
      components: {
        default: () => import("./views/Search.vue")
      },
      props: { default: true }
    },
    {
      // path: "/:username",
      path: "/user/:username",
      components: {
        default: () => import("./views/Profile.vue")
      },
      props: { default: true },
      children: [
        {
          path: "",
          name: "recents",
          components: {
            default: () => import("./views/Recents.vue")
          },
          props: { default: true }
        },
        {
          // @check
          path: "tree/:bm_id([\\d\\w]+)",
          // path: "tree/:bm_id([\\d\\w]+)+",
          name: "tree",
          components: {
            default: () => import("./views/BookmarkView.vue")
          },
          props: { default: true }
        }
      ]
    }
  ]
});

router.afterEach(() => {
  store.commit("clearMove");
});

export default router;
