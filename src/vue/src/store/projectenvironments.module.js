import { projectenvironmentService } from "../services";
import Vue from "vue";

export const projectenvironments = {
  namespaced: true,
  state: {
    all: { environments_dicts: {} },
    status: {}
  },
  actions: {
    creating({ dispatch, commit }, { project_id, newenvname }) {
      commit("creatingRequest", {});
      projectenvironmentService.create(project_id, newenvname).then(
        environment => {
          commit("creatingSuccess", { environment, project_id });
        },
        error => {
          commit("creatingFailure", error);
          dispatch("alert/error", error, { root: true });
        }
      );
    },
    updating(
      { dispatch, commit },
      { project_id, envid, envname, envvalue, envdescription }
    ) {
      commit("updatingRequest", {});
      projectenvironmentService
        .update(envid, envname, envvalue, envdescription)
        .then(
          environment => {
            commit("updatingSuccess", { environment, project_id });
          },
          error => {
            commit("updatingFailure", error);
            dispatch("alert/error", error, { root: true });
          }
        );
    },
    getAll({ commit }, { project_id }) {
      commit("getAllRequest", project_id);
      projectenvironmentService.getAll(project_id).then(
        environments => commit("getAllSuccess", { environments, project_id }),
        error => commit("getAllFailure", error)
      );
    }
  },
  mutations: {
    creatingRequest(state) {
      state.status = { creating: true };
    },
    creatingSuccess(state, p) {
      var env = p.environment["environment"];
      var project_id = p.project_id;
      state.status = { created: true };
      env.untouched = true;
      !(project_id in state.all.environments_dicts) &&
        Vue.set(state.all.environments_dicts, project_id, {});
      !("environments" in state.all.environments_dicts[project_id]) &&
        Vue.set(state.all.environments_dicts[project_id], "environments", {});
      Vue.set(
        state.all.environments_dicts[project_id]["environments"],
        env.id,
        env
      );
    },
    creatingFailure(state) {
      state.status = {};
      state.user = null;
    },
    updatingRequest(state) {
      state.status = { updating: true };
    },
    updatingSuccess(state, p) {
      var env = p.environment["environment"];
      var project_id = p.project_id;
      state.status = { updated: true };
      env.untouched = true;
      !(project_id in state.all.environments_dicts) &&
        Vue.set(state.all.environments_dicts, project_id, {});
      !("environments" in state.all.environments_dicts[project_id]) &&
        Vue.set(state.all.environments_dicts[project_id], "environments", {});
      Vue.set(
        state.all.environments_dicts[project_id]["environments"],
        env.id,
        env
      );
    },
    updatingFailure(state) {
      state.status = {};
      state.user = null;
    },
    getAllRequest(state, project_id) {
      Vue.set(state.all.environments_dicts, project_id, { loading: true });
    },
    getAllSuccess(state, p) {
      var envs = p.environments["environments"];
      var project_id = p.project_id;
      envs.forEach(function(element) {
        element.untouched = true;
        !(project_id in state.all.environments_dicts) &&
          Vue.set(state.all.environments_dicts, project_id, {});
        !("environments" in state.all.environments_dicts[project_id]) &&
          Vue.set(state.all.environments_dicts[project_id], "environments", {});
        Vue.set(
          state.all.environments_dicts[project_id]["environments"],
          element.id,
          element
        );
      });
      Vue.delete(state.all.environments_dicts[project_id], "loading");
    },
    getAllFailure(state, error) {
      state.all = { error };
    }
  }
};
