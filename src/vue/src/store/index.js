import Vue from 'vue';
import Vuex from 'vuex';

import { alert } from './alert.module';
import { authentication } from './authentication.module';
import { users } from './users.module';
import { projects } from './projects.module';

Vue.use(Vuex);

const store = new Vuex.Store({
    modules: {
        alert,
        authentication,
        users,
	projects
    }
});

export default store;
