import { projectService } from "../services";
import Vue from "vue";
import router from '../router/';

export const projects = {
  namespaced: true,
  state: {
    all: { projects_dict : {} },
    status : {}
  },
  actions: {
    creating({ dispatch, commit }, { projectname }) {
      commit("creatingRequest", {});
        projectService.create(projectname).then(
          project => {
            commit("creatingSuccess", project);
            router.push({
              name: 'ProjectSettings',
              params: { project_id: project.id }
            });
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
    },
    get({ commit }, { project_id}) {
      commit("getRequest");

      projectService.get(project_id).then(
        project => commit("getSuccess", project["project"]),
        error => commit("getFailure", error)
      );
    }
  },
  mutations: {
    creatingRequest(state) {
      state.status = { creating: true };
    },
    creatingSuccess(state, project) {
      state.status = { created: true };
      state.all.projects_dict[project.id] = project;
    },
    creatingFailure(state) {
      state.status = {};
      state.user = null;
    },
    getAllRequest(state) {
      state.all = { loading: true };
    },
    getRequest(state) {
      state.all.loading = true ;
    },
    getAllSuccess(state, projects) {
      const projects_dict = {}
      projects.forEach((element) => projects_dict[element.id] = element);
      state.all = { projects_dict };
    },
    getSuccess(state, project) {
      console.log(project);
      Vue.set(state.all.projects_dict, project.id, project);
      Vue.delete(state.all, 'loading');
    },
    getAllFailure(state, error) {
      state.all = { error };
    },
    getFailure(state, error) {
      state.all = { error };
    }
  }
};
