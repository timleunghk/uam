import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule, APP_INITIALIZER } from '@angular/core';
import { HttpClientModule, HTTP_INTERCEPTORS, HttpClientXsrfModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { CustStyleModule } from './cust-style.module';
import { RequestsListComponent } from './requests/requests-list/requests-list.component';
import { RequestsDetailNewAccountComponent } from './requests/requests-detail-account-new/requests-detail-account-new.component';
import { RequestPopupContainerComponent } from './requests/request-popup-container/request-popup-container.component';
import { MessageService, ConfirmationService } from 'primeng/api'
import { RequestsDetailNewAccountReviewComponent } from './requests/requests-detail-account-review/requests-detail-account-review.component';
import { BasicUserInfoComponent } from './requests/basic-user-info/basic-user-info.component';
import { UserInfoSystemsComponent } from './requests/user-info-systems/user-info-systems.component';
import { RequestsDetailNewAccountExecuteComponent } from './requests/requests-detail-account-execute/requests-detail-account-execute.component';
import { FormatDatePipe } from './judCommon/formatDate.pipe';
import { RequestNewContainerComponent } from './requests/request-new-container/request-new-container.component';
import { AuditLogListComponent } from './requests/audit-log-list/audit-log-list.component';
import { DropdownModule } from 'primeng/dropdown';
import { AccountsDisableComponent } from './accounts/accounts-disable/accounts-disable.component';
import { AccountsEnableComponent } from './accounts/accounts-enable/accounts-enable.component';
import { AccountsDeleteComponent } from './accounts/accounts-delete/accounts-delete.component';
import { AccountsEnquiryListComponent } from './accounts/accounts-enquiry-list/accounts-enquiry-list.component';
import { AccountEnquiryContentComponent } from './accounts/account-enquiry-content/account-enquiry-content.component';
import { RequestsUpdateAccountListComponent } from './requests/requests-update-account-list/requests-update-account-list.component';
import { PasswordResetComponent } from './accounts/password-reset/password-reset.component';
import { PersonalProfilesComponent } from './accounts/personal-profiles/personal-profiles.component';
import { JudDialogComponent } from './judCommon/jud-dialog.component'
import { RequestsToDoListComponent } from './requests/requests-todolist/requests-todolist.component';
import { RequestsSetupCompleteComponent } from './requests/requests-setup-complete/requests-setup-complete.component';
import { RequestsUserAckComponent } from './requests/requests-user-ack/requests-user-ack.component';
import { DisableControlDirective } from './judCommon/disable-control.directive'
import { AutofocusDirective } from './judCommon/autofocus-control.directive'
// import { AppConfigService } from './judCommon/config-service';
import { RequestFlowComponent } from './requests/request-flow/request-flow.component';
import { StepsModule } from 'primeng/steps';
import { PickListModule } from 'primeng/picklist';
import { FileMaintainerComponent } from './requests/file-maintainer/file-maintainer.component';
import { NgMathPipesModule, BytesPipe } from 'angular-pipes';
import { TitleCasePipe, UpperCasePipe } from '@angular/common';
// import { HttpAuthInterceptor, HttpXsrfInterceptor } from './judCommon/httpAuthInterceptor';
import { CookieService } from 'ngx-cookie-service';

@NgModule({
  declarations: [
    AppComponent,
    RequestsToDoListComponent,
    RequestsListComponent,
    RequestsDetailNewAccountComponent,
    RequestPopupContainerComponent,
    DisableControlDirective,
    RequestsDetailNewAccountReviewComponent,
    BasicUserInfoComponent,
    UserInfoSystemsComponent,
    RequestsDetailNewAccountExecuteComponent,
    FormatDatePipe,
    RequestNewContainerComponent,
    AuditLogListComponent,
    AccountsDisableComponent,
    AccountsEnableComponent,
    AccountsDeleteComponent,
    AccountsEnquiryListComponent,
    AccountEnquiryContentComponent,
    PasswordResetComponent,
    RequestsUpdateAccountListComponent,
    PersonalProfilesComponent,
    JudDialogComponent,
    RequestsSetupCompleteComponent,
    RequestsUserAckComponent,
    AutofocusDirective,
    RequestFlowComponent,
    FileMaintainerComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    CustStyleModule,
    HttpClientModule,
    FormsModule, ReactiveFormsModule,
    AutoCompleteModule,
    DropdownModule,
    FormsModule,
    StepsModule,
    NgMathPipesModule,
    HttpClientXsrfModule.withOptions({
      cookieName: 'csrftoken',
      headerName: 'X-CSRFToken',
    }),
    PickListModule,
  ],

  exports: [
    AutoCompleteModule
  ],

  providers: [
    MessageService
    , ConfirmationService
    // , {
    //   provide: APP_INITIALIZER,
    //   multi: true,
    //   deps: [AppConfigService],
    //   useFactory: (appConfigService: AppConfigService) => {
    //     return () => {
    //       return appConfigService.loadAppConfig();
    //     }; 1
    //   }
    // },
    ,
    BytesPipe,
    // { provide: HTTP_INTERCEPTORS, useClass: HttpAuthInterceptor, multi: true },
    // { provide: HTTP_INTERCEPTORS, useClass: HttpXsrfInterceptor, multi: true },
    CookieService,
    TitleCasePipe, UpperCasePipe,
  ],


  bootstrap: [AppComponent]
})
export class AppModule { }


