import Vue from "vue";
import Vuex from "vuex";

import { alert } from "./alert.module";
import { authentication } from "./authentication.module";
import { users } from "./users.module";
import { projects } from "./projects.module";
import { projectsettings } from "./projectsettings.module";
import { settings } from "./settings.module";
import { executions } from "./executions.module";

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    alert,
    authentication,
    users,
    projects,
    projectsettings,
    executions,
    settings
  }
});

export default store;
