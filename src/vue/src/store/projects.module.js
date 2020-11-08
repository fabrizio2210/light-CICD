import { projectService } from "../services";

export const projects = {
  namespaced: true,
  state: {
    all: {}
  },
  actions: {
    getAll({ commit }) {
      commit("getAllRequest");

      projectService.getAll().then(
        projects => commit("getAllSuccess", projects["projects"]),
        error => commit("getAllFailure", error)
      );
    }
  },
  mutations: {
    getAllRequest(state) {
      state.all = { loading: true };
    },
    getAllSuccess(state, projects) {
      state.all = { projects };
    },
    getAllFailure(state, error) {
      state.all = { error };
    }
  }
};
