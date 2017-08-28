import alertify from 'alertifyjs';
import {dataInterface} from './dataInterface';
import {
  log,
  t,
  notify,
  redirectTo,
} from './utils';

var Reflux = require('reflux');

var actions = {};


actions.navigation = Reflux.createActions([
    'transitionStart',
    'transitionEnd',
    'historyPush',
    'routeUpdate',

    'documentTitleUpdate'
  ]);

actions.auth = Reflux.createActions({
  login: {
    children: [
      'loggedin',
      'passwordfail',
      'anonymous',
      'failed'
    ]
  },
  verifyLogin: {
    children: [
      'loggedin',
      'anonymous',
      'failed'
    ]
  },
  logout: {
    children: [
      'completed',
      'failed'
    ]
  }
});

actions.survey = Reflux.createActions({
  addItemAtPosition: {
    children: [
      'completed',
      'failed'
    ],
  }
});

actions.search = Reflux.createActions({
  assets: {
    children: [
      'completed',
      'failed'
    ]
  },
  assetsWithTags: {
    children: [
      'completed',
      'failed'
    ]
  },
  tags: {
    children: [
      'completed',
      'failed'
    ]
  },
  libraryDefaultQuery: {
    children: [
      'completed',
      'failed'
    ]
  },
  collections: {
    children: [
      'completed',
      'failed'
    ]
  }
});

actions.resources = Reflux.createActions({
  listAssets: {
    children: [
      'completed',
      'failed'
    ]
  },
  listSurveys: {
    children: [
      'completed',
      'failed'
    ]
  },
  listCollections: {
    children: [
      'completed',
      'failed'
    ]
  },
  listQuestionsAndBlocks: {
    children: [
      'completed',
      'failed'
    ]
  },
  createAsset: {
    children: [
      'completed',
      'failed'
    ]
  },
  createImport: {
    children: [
      'completed',
      'failed'
    ]
  },
  loadAsset: {
    children: [
      'completed',
      'failed'
    ]
  },
  deployAsset: {
    children: [
      'completed',
      'failed'
    ]
  },
  createSnapshot: {
    children: [
      'completed',
      'failed'
    ]
  },
  cloneAsset: {
    children: [
      'completed',
      'failed'
    ]
  },
  deleteAsset: {
    children: [
      'completed',
      'failed'
    ]
  },
  listTags: {
    children: [
      'completed',
      'failed'
    ]
  },
  createCollection: {
    children: [
      'completed',
      'failed'
    ]
  },
  readCollection: {
    children: [
      'completed',
      'failed'
    ]
  },
  updateCollection: {
    children: [
      'completed',
      'failed'
    ]
  },
  deleteCollection: {
    children: [
      'completed',
      'failed'
    ]
  },
  loadAssetSubResource: {
    children: [
      'completed',
      'failed'
    ]
  },
  loadAssetContent: {
    children: [
      'completed',
      'failed'
    ]
  },
  loadResource: {
    children: [
      'completed',
      'failed'
    ],
  },
  createResource: {
    children: [
      'completed',
      'failed'
    ]
  },
  updateAsset: {
    children: [
      'completed',
      'failed'
    ]
  },
  notFound: {}
});

actions.permissions = Reflux.createActions({
  assignPerm: {
    children: [
      'completed',
      'failed'
    ]
  },
  removePerm: {
    children: [
      'completed',
      'failed'
    ]
  },
  assignPublicPerm: {
    children: [
      'completed',
      'failed'
    ]
  },
  setCollectionDiscoverability: {
    children: [
      'completed',
      'failed'
    ]
  },
});

actions.misc = Reflux.createActions({
  checkUsername: {
    asyncResult: true,
    children: [
      'completed',
      'failed_'
    ]
  }
});


actions.misc.checkUsername.listen(function(username){
  dataInterface.queryUserExistence(username)
    .done(actions.misc.checkUsername.completed)
    .fail(actions.misc.checkUsername.failed_);
});
actions.resources.createImport.listen(function(contents){
  if (contents.base64Encoded) {
    dataInterface.postCreateBase64EncodedImport(contents)
      .done(actions.resources.createImport.completed)
      .fail(actions.resources.createImport.failed);
  } else if (contents.content) {
    dataInterface.createResource(contents);
  }
});

actions.resources.createImport.completed.listen(function(contents){
  if (contents.status) {
    if(contents.status === 'processing') {
      notify(t('successfully uploaded file; processing may take a few minutes'));
      log('processing import ' + contents.uid, contents);
    } else {
      notify(`unexpected import status ${contents.status}`, 'error');
    }
  } else {
    notify(t('Error: import.status not available'));
  }
});

actions.resources.createAsset.listen(function(){
  console.error(`use actions.resources.createImport
                  or actions.resources.createResource.`);
});

actions.resources.createResource.failed.listen(function(){
  log('createResourceFailed');
});

actions.resources.createSnapshot.listen(function(details){
  dataInterface.createAssetSnapshot(details)
    .done(actions.resources.createSnapshot.completed)
    .fail(actions.resources.createSnapshot.failed);
});

actions.resources.listTags.listen(function(data){
  dataInterface.listTags(data)
    .done(actions.resources.listTags.completed)
    .fail(actions.resources.listTags.failed);
});

actions.resources.listTags.completed.listen(function(results){
  if (results.next) {
    if (window.trackJs) {
      window.trackJs.track('MAX_TAGS_EXCEEDED: Too many tags');
    }
  }
});

actions.resources.updateAsset.listen(function(uid, values){
  return new Promise(function(resolve, reject){
    dataInterface.patchAsset(uid, values)
      .done(function(asset){
      //dataInterface.deployAsset(asset, true);
        actions.resources.deployAsset(asset, true);
        //notify(t('successfully updated'));
        //resolve(asset);
      })
      .fail(function(...args){
        reject(args)
      });
  })
});

actions.resources.deployAsset.listen(
  function(asset, redeployment, dialog_or_alert){
    dataInterface.deployAsset(asset, redeployment)
      .done((data) => {
        actions.resources.deployAsset.completed(data, dialog_or_alert);
      })
      .fail((data) => {
        actions.resources.deployAsset.failed(data, dialog_or_alert);
      });
  }
);

actions.resources.deployAsset.completed.listen(function(data, dialog_or_alert){
  // close the dialog/alert.
  // (this was sometimes failing. possibly dialog already destroyed?)
  if (dialog_or_alert) {
    if (typeof dialog_or_alert.destroy === 'function') {
        dialog_or_alert.destroy();
    } else if (typeof dialog_or_alert.dismiss === 'function') {
        dialog_or_alert.dismiss();
    }
  }
  // notify and redirect
  notify(t('deployed form'));
  window.setTimeout(function(){
    redirectTo(data.identifier);
  }, 1000);
});

actions.resources.deployAsset.failed.listen(function(data, dialog_or_alert){
  // close the dialog/alert.
  // (this was sometimes failing. possibly dialog already destroyed?)
  if (dialog_or_alert) {
    if (typeof dialog_or_alert.destroy === 'function') {
        dialog_or_alert.destroy();
    } else if (typeof dialog_or_alert.dismiss === 'function') {
        dialog_or_alert.dismiss();
    }
  }
  // report the problem to the user
  let failure_message = null;

  if(!data.responseJSON || (!data.responseJSON.xform_id_string &&
                            !data.responseJSON.detail)) {
    // failed to retrieve a valid response from the server
    // setContent() removes the input box, but the value is retained
    var msg;
    if (data.status == 500 && data.responseJSON && data.responseJSON.error) {
      msg = `<code><pre>${data.responseJSON.error}</pre></code>`;
    } else if (data.status == 500 && data.responseText) {
      msg = `<code><pre>${data.responseText}</pre></code>`;
    } else {
      msg = t('please check your connection and try again.');
    }
    failure_message = `
      <p>${msg}</p>
      <p>${t('if this problem persists, contact support@kobotoolbox.org')}</p>
    `;
  } else if(!!data.responseJSON.xform_id_string){
    // TODO: now that the id_string is automatically generated, this failure
    // mode probably doesn't need special handling
    failure_message = `
      <p>${t('the form id was not valid.')}</p>
      <p>${t('if this problem persists, contact support@kobotoolbox.org')}</p>
      <p><code>${data.responseJSON.xform_id_string}</code></p>
    `;
  } else if(!!data.responseJSON.detail) {
    failure_message = `
      <p>${t('your form cannot be deployed because it contains errors:')}</p>
      <p><code>${data.responseJSON.detail}</code></p>
    `;
  }
  alertify.alert(t('unable to deploy'), failure_message);
});

actions.resources.createResource.listen(function(details){
  return new Promise(function(resolve, reject){
    dataInterface.createResource(details)
      .done(function(asset){
        //actions.resources.createResource.completed(asset);
        window.setTimeout(function(){
    actions.resources.deployAsset(asset);
  }, 500);
        //resolve(asset);
      })
      .fail(function(...args){
        actions.resources.createResource.failed(...args)
        reject(args);
      });
  });
});

actions.resources.deleteAsset.listen(function(details, params={}){
  var onComplete;
  if (params && params.onComplete) {
    onComplete = params.onComplete;
  }
  dataInterface.deleteAsset(details)
    .done(function(/*result*/){
      actions.resources.deleteAsset.completed(details);
      if (onComplete) {
        onComplete(details);
      }
    })
    .fail(actions.resources.deleteAsset.failed);
});
actions.resources.readCollection.listen(function(details){
  dataInterface.readCollection(details)
      .done(actions.resources.readCollection.completed)
      .fail(function(req, err, message){
        actions.resources.readCollection.failed(details, req, err, message);
      });
});

actions.resources.deleteCollection.listen(function(details){
  dataInterface.deleteCollection(details)
    .done(function(result){
      actions.resources.deleteCollection.completed(details, result);
    })
    .fail(actions.resources.deleteCollection.failed);
});

actions.resources.updateCollection.listen(function(uid, values){
  return new Promise(function(resolve, reject){
    dataInterface.patchCollection(uid, values)
      .done(function(asset){
        actions.resources.updateCollection.completed(asset);
        notify(t('successfully updated'));
        resolve(asset);
      })
      .fail(function(...args){
        reject(args)
      });
  })
});

actions.resources.cloneAsset.listen(function(details, opts={}){
  dataInterface.cloneAsset(details)
    .done(function(...args){
      actions.resources.createAsset.completed(...args);
      actions.resources.cloneAsset.completed(...args);
      if (opts.onComplete) {
        opts.onComplete(...args);
      }
    })
    .fail(actions.resources.cloneAsset.failed);
});

actions.search.assets.listen(function(queryString){
  dataInterface.searchAssets(queryString)
    .done(function(...args){
      actions.search.assets.completed.apply(this, [queryString, ...args]);
    })
    .fail(function(...args){
      actions.search.assets.failed.apply(this, [queryString, ...args]);
    });
});

actions.search.libraryDefaultQuery.listen(function(){
  dataInterface.libraryDefaultSearch()
    .done(actions.search.libraryDefaultQuery.completed)
    .fail(actions.search.libraryDefaultQuery.failed);
});

actions.search.assetsWithTags.listen(function(queryString){
  dataInterface.assetSearch(queryString)
    .done(actions.search.assetsWithTags.completed)
    .fail(actions.search.assetsWithTags.failed);
});

actions.search.tags.listen(function(queryString){
  dataInterface.searchTags(queryString)
    .done(actions.search.searchTags.completed)
    .fail(actions.search.searchTags.failed);
});

actions.permissions.assignPerm.listen(function(creds){
  dataInterface.assignPerm(creds)
    .done(actions.permissions.assignPerm.completed)
    .fail(actions.permissions.assignPerm.failed);
});
actions.permissions.assignPerm.completed.listen(function(val){
  actions.resources.loadAsset({url: val.content_object});
});

actions.permissions.removePerm.listen(function(details){
  if (!details.content_object_uid) {
    throw new Error('removePerm needs a content_object_uid parameter to be set');
  }
  dataInterface.removePerm(details.permission_url)
    .done(function(resp){
      actions.permissions.removePerm.completed(details.content_object_uid, resp);
    })
    .fail(actions.permissions.removePerm.failed);
});

actions.permissions.removePerm.completed.listen(function(uid){
  actions.resources.loadAsset({id: uid});
});

actions.permissions.setCollectionDiscoverability.listen(function(uid, discoverable){
  dataInterface.patchCollection(uid, {discoverable_when_public: discoverable})
    .done(actions.permissions.setCollectionDiscoverability.completed)
    .fail(actions.permissions.setCollectionDiscoverability.failed);
});
actions.permissions.setCollectionDiscoverability.completed.listen(function(val){
  actions.resources.loadAsset({url: val.url});
});

actions.auth.login.listen(function(creds){
  dataInterface.login(creds).done(function(resp1){
    dataInterface.selfProfile().done(function(data){
        if(data.username) {
          actions.auth.login.loggedin(data);
        } else {
          actions.auth.login.passwordfail(resp1);
        }
      }).fail(actions.auth.login.failed);
  })
    .fail(actions.auth.login.failed);
});

// reload so a new csrf token is issued
actions.auth.logout.completed.listen(function(){
  window.setTimeout(function(){
    window.location.replace('', '');
  }, 1);
});

actions.auth.logout.listen(function(){
  dataInterface.logout().done(actions.auth.logout.completed).fail(function(){
    console.error('logout failed for some reason. what should happen now?');
  });
});
actions.auth.verifyLogin.listen(function(){
    dataInterface.selfProfile()
        .done((data/*, msg, req*/)=>{
          if (data.username) {
            actions.auth.verifyLogin.loggedin(data);
          } else {
            actions.auth.verifyLogin.anonymous(data);
          }
        })
        .fail(actions.auth.verifyLogin.failed);
});

actions.resources.loadAsset.listen(function(params){
  var dispatchMethodName;
  if (params.url) {
    dispatchMethodName = params.url.indexOf('collections') === -1 ?
        'getAsset' : 'getCollection';
  } else {
    dispatchMethodName = {
      c: 'getCollection',
      a: 'getAsset'
    }[params.id[0]];
  }

  dataInterface[dispatchMethodName](params)
      .done(actions.resources.loadAsset.completed)
      .fail(actions.resources.loadAsset.failed);
});

actions.resources.loadAsset.completed.listen(function(asset){
  actions.navigation.historyPush(asset);
});

actions.resources.loadAssetContent.listen(function(params){
  dataInterface.getAssetContent(params)
      .done(function(data, ...args) {
        // data.sheeted = new Sheeted([['survey', 'choices', 'settings'], data.data])
        actions.resources.loadAssetContent.completed(data, ...args);
      })
      .fail(actions.resources.loadAssetContent.failed);
});

actions.resources.listAssets.listen(function(){
  dataInterface.listAllAssets()
      .done(actions.resources.listAssets.completed)
      .fail(actions.resources.listAssets.failed);
});

actions.resources.listSurveys.listen(function(){
  dataInterface.listSurveys()
      .done(actions.resources.listAssets.completed)
      .fail(actions.resources.listAssets.failed);
});

actions.resources.listCollections.listen(function(){
  dataInterface.listCollections()
      .done(actions.resources.listCollections.completed)
      .fail(actions.resources.listCollections.failed);
});

actions.resources.listQuestionsAndBlocks.listen(function(){
  dataInterface.listQuestionsAndBlocks()
      .done(actions.resources.listAssets.completed)
      .fail(actions.resources.listAssets.failed);
});

module.exports = actions;
