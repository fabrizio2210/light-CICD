import { executionService } from "../services";
import Vue from "vue";

export const executions = {
  namespaced: true,
  state: {
    all: { executions_dicts: {} },
    status: {}
  },
  actions: {
    executing({ dispatch, commit }, { project_id }) {
      commit("executingRequest", {});
      executionService.exec(project_id).then(
        execution => {
          commit("executingSuccess", execution["execution"]);
          dispatch("alert/success", "", { root: true });
        },
        error => {
          commit("executingFailure", error);
          dispatch("alert/error", error, { root: true });
        }
      );
    },
    getAll({ commit }, { project_id }) {
      commit("getAllRequest", project_id);

      executionService.getAll(project_id).then(
        executions => {
          commit("getAllSuccess", { executions, project_id });
        },
        error => commit("getAllFailure", error)
      );
    },
    get({ commit }, { project_id, execution_id }) {
      executionService.get(project_id, execution_id).then(
        execution => { 
          commit("getSuccess", { execution, project_id });
        },
        error => commit("getFailure", error)
      );
    }
  },
  mutations: {
    executingRequest(state) {
      state.status = { executing: true };
    },
    executingSuccess(state, execution) {
      state.status = { executed: true };
      !(execution.project_id in state.all.executions_dicts) &&
        Vue.set(state.all.executions_dicts, execution.project_id, {});
      !("executions" in state.all.executions_dicts[execution.project_id]) &&
        Vue.set(
          state.all.executions_dicts[execution.project_id],
          "executions",
          {}
        );
      Vue.set(
        state.all.executions_dicts[execution.project_id]["executions"],
        execution.id,
        execution
      );
    },
    executingFailure(state) {
      state.status = {};
      state.user = null;
    },
    getAllRequest(state, project_id) {
      Vue.set(state.all.executions_dicts, project_id, { loading: true });
    },
    getAllSuccess(state, p) {
      var executions = p.executions["executions"];
      executions.forEach(function(element) {
        !(element.project_id in state.all.executions_dicts) &&
          Vue.set(state.all.executions_dicts, element.project_id, {});
        !("executions" in state.all.executions_dicts[element.project_id]) &&
          Vue.set(
            state.all.executions_dicts[element.project_id],
            "executions",
            {}
          );
        Vue.set(
          state.all.executions_dicts[element.project_id]["executions"],
          element.id,
          element
        );
      });
      Vue.delete(state.all.executions_dicts[p.project_id], "loading");
    },
    getAllFailure(state, error) {
      state.all = { error };
    },
    getSuccess(state, p) {
      var execution = p.execution["execution"];
      !(execution.project_id in state.all.executions_dicts) &&
        Vue.set(state.all.executions_dicts, execution.project_id, {});
      !("executions" in state.all.executions_dicts[execution.project_id]) &&
        Vue.set(
          state.all.executions_dicts[execution.project_id],
          "executions",
          {}
        );
      Vue.set(
        state.all.executions_dicts[execution.project_id]["executions"],
        execution.id,
        execution
      );
      Vue.delete(state.all.executions_dicts[p.project_id], "loading");
    },
    getFailure(state, error) {
      state.all = { error };
    }
  }
};
