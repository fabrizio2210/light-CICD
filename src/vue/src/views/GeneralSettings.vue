<template>
    <div>
        <h3>Settings from secure api end point:</h3>
        <em v-if="settings.loading">Loading settings...</em>
        <img v-show="settings.loading" src="../assets/loading.gif" />
        <span v-if="settings.error" class="text-danger">ERROR: {{settings.error}}</span>
        <ul v-if="settings.settings">
            <li v-for="setting in settings.settings" :key="setting.id">
                <form @submit.prevent="handleSubmit">
                    <div class="form-group">
                        <label for="settingname">{{setting.id + '. ' + setting.description + ': '}}</label>
                        <input type="text" v-model="setting.value" :placeholder="setting.default_value" name="settingname" class="form-control" />
                        <button class="btn btn-primary" :disabled="updating" >Update</button>
                    </div>
                </form>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    data () {
        return {
            settingname: '',
            submitted: false
        }
    },
    computed: {
        user () {
            return this.$store.state.authentication.user;
        },
        updating () {
            return this.$store.state.settings.status.updating;
        },
        settings () {
            return this.$store.state.settings.all;
        }
    },
    methods: {
        handleSubmit () {
            this.submitted = true;
            const { settingname } = this;
            const { dispatch } = this.$store;
            if (settingname) {
                dispatch('settings/updating', { settingname });
            }
        }
    },
    created () {
        this.$store.dispatch('settings/getAll');
    }
};
</script>
