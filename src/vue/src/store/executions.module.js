import { executionService } from "../services";

export const executions = {
  namespaced: true,
  state: {
    all: {},
    status : {}
  },
  actions: {
    executing({ dispatch, commit }, { project_id }) {
      commit("executingRequest", { });
        executionService.execute(project_id).then(
          execution => {
            commit("executingSuccess", execution);
          },
          error => {
            commit("executingFailure", error);
            dispatch("alert/error", error, { root: true});
          }
        );
      },
    getAll({ commit }, { project_id }) {
      commit("getAllRequest");

      executionService.getAll(project_id).then(
        executions => commit("getAllSuccess", executions["executions"]),
        error => commit("getAllFailure", error)
      );
    }
  },
  mutations: {
    executingRequest(state) {
      state.status = { executing: true };
    },
    executingSuccess(state, execution) {
      state.status = { executed: true };
      state.all.executions_dicts[execution.project_id][execution.id] = execution;
    },
    executingFailure(state) {
      state.status = {};
      state.user = null;
    },
    getAllRequest(state) {
      state.all = { loading: true };
    },
    getAllSuccess(state, executions) {
      //const executions_dict = {}
      //executions.forEach((element) => executions_dict[element.name] = element);
      //state.all = { executions_dict };
      //TODO verify if it works
      executions.forEach((element) => state.all.executions_dicts[element.project_id][element.name] = element);
      console.log(executions);
      console.log(state.all);
    },
    getAllFailure(state, error) {
      state.all = { error };
    }
  }
};
