import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { RequestsListComponent } from './requests/requests-list/requests-list.component';
import { RequestNewContainerComponent } from './requests/request-new-container/request-new-container.component';
import { AccountsDisableComponent } from './accounts/accounts-disable/accounts-disable.component';
import { AccountsEnableComponent } from './accounts/accounts-enable/accounts-enable.component';
import { AccountsDeleteComponent } from './accounts/accounts-delete/accounts-delete.component';
import { AccountsEnquiryListComponent } from './accounts/accounts-enquiry-list/accounts-enquiry-list.component';
import { PasswordResetComponent } from './accounts/password-reset/password-reset.component';
import { RequestsUpdateAccountListComponent } from './requests/requests-update-account-list/requests-update-account-list.component';
import { PersonalProfilesComponent } from './accounts/personal-profiles/personal-profiles.component';
import { RequestsToDoListComponent } from './requests/requests-todolist/requests-todolist.component';
import { RequestsSetupCompleteComponent } from './requests/requests-setup-complete/requests-setup-complete.component';
import { RequestsUserAckComponent } from './requests/requests-user-ack/requests-user-ack.component';

const routes: Routes = [
  // {
  //   path: 'create-account',
  //   component: CreateAccountComponent
  // },
  // {
  //   path: 'create-account-detail/:id',
  //   component: CreateAccountComponent
  // },



  {
    path: 'to-do-list',
    component: RequestsToDoListComponent,
    // children: [
    //   { path: ':id/create-account-detail', component: RequestPopupContainerComponent }
    // ]
  },  

  {
    path: 'new-request',
    component: RequestNewContainerComponent,
    // children: [
    //   { path: ':id/create-account-detail', component: RequestPopupContainerComponent }
    // ]
  },
  {
    path: 'requests',
    component: RequestsListComponent,
    // children: [
    //   { path: ':id/create-account-detail', component: RequestPopupContainerComponent }
    // ]
  },
  {
    path: 'password-reset',
    component: PasswordResetComponent,
  },   
  {
    path: 'accounts-update',
    component: RequestsUpdateAccountListComponent,
  },    
  {
    path: 'accounts-enquiry',
    component: AccountsEnquiryListComponent,
  },  
  {
    path: 'accounts-delete',
    component: AccountsDeleteComponent,
  },
  {
    path: 'accounts-enable',
    component: AccountsEnableComponent,
  },  

  {
    path: 'accounts-disable',
    component: AccountsDisableComponent,
  },  
  
  {
    path: 'personal-profiles',
    component: PersonalProfilesComponent,
  },  
  {
    path: 'setup-complete',
    component: RequestsSetupCompleteComponent,
    // children: [
    //   { path: ':id/create-account-detail', component: RequestPopupContainerComponent }
    // ]
  },  

  {
    path: 'user-ack',
    component: RequestsUserAckComponent,
    // children: [
    //   { path: ':id/create-account-detail', component: RequestPopupContainerComponent }
    // ]
  }, 
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
