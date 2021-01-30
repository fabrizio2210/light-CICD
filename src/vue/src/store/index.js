import Vue from "vue";
import Vuex from "vuex";

import { alert } from "./alert.module";
import { authentication } from "./authentication.module";
import { users } from "./users.module";
import { projects } from "./projects.module";
import { projectsettings } from "./projectsettings.module";
import { projectenvironments } from "./projectenvironments.module";
import { settings } from "./settings.module";
import { executions } from "./executions.module";
import { executionoutputs } from "./executionoutputs.module";

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    alert,
    authentication,
    users,
    projects,
    projectenvironments,
    projectsettings,
    executions,
    executionoutputs,
    settings
  }
});

export default store;
