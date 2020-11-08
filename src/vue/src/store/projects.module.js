import { projectService } from "../services";

export const projects = {
  namespaced: true,
  state: {
    all: {},
    status : {}
  },
  actions: {
    creating({ dispatch, commit }, { projectname }) {
      commit("creatingRequest", { });
        projectService.create(projectname).then(
          project => {
            commit("creatingSuccess", project);
          },
          error => {
            commit("creatingFailure", error);
            dispatch("alert/error", error, { root: true});
          }
        );
      },
    getAll({ commit }) {
      commit("getAllRequest");

      projectService.getAll().then(
        projects => commit("getAllSuccess", projects["projects"]),
        error => commit("getAllFailure", error)
      );
    }
  },
  mutations: {
    creatingRequest(state) {
      state.status = { creating: true };
    },
    creatingSuccess(state, project) {
      state.status = { created: true };
      state.all.projects.push(project);
    },
    creatingFailure(state) {
      state.status = {};
      state.user = null;
    },
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
