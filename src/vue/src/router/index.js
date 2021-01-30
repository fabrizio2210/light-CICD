import Vue from "vue";
import VueRouter from "vue-router";

import HomePage from "../views/HomePage.vue";
import GeneralSettings from "../views/GeneralSettings.vue";
import ProjectExecutions from "../views/ProjectExecutions.vue";
import ProjectEnvironments from "../views/ProjectEnvironments.vue";
import ProjectSettings from "../views/ProjectSettings.vue";
import ExecutionOutput from "../views/ExecutionOutput.vue";
import Project from "../views/Project.vue";
import LoginPage from "../views/Login.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomePage
  },
  {
    path: '/projects/:project_id',
    component: Project,
    children: [
      {
        path: '',
        name: "Executions",
        component: ProjectExecutions,
      },
      {
        path: 'executions/:exec_id/output',
        name: 'ExecutionOutput',
        component: ExecutionOutput
      },
      {
        path: 'environments',
        name: "ProjectEnvironments",
        component: ProjectEnvironments
      },
      {
        path: 'settings',
        name: 'ProjectSettings',
        component: ProjectSettings
      }
    ]
  },
  {
    path: "/settings",
    name: "Settings",
    component: GeneralSettings
  },
  {
    path: "/login",
    name: "Login",
    component: LoginPage
  },
  // otherwise redirect to home
  { path: "*", redirect: "/" }
];

const router = new VueRouter({
  mode: "history",
  routes
});

export default router;

router.beforeEach((to, from, next) => {
  // redirect to login page if not logged in and trying to access a restricted page
  const publicPages = ["/login"];
  const authRequired = !publicPages.includes(to.path);
  const loggedIn = localStorage.getItem("user");

  if (authRequired && !loggedIn) {
    return next("/login");
  }

  next();
});
